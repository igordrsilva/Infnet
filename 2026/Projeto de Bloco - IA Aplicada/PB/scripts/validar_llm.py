"""Validação ponta a ponta com a LLM REAL (Qwen2.5-3B local) e dados reais.

Uso (na raiz do projeto, com o modelo já baixado):
    python scripts/validar_llm.py

Roda as 4 funções de IA do projeto (resumo de notícia, resumo de dados, perguntas sobre os dados e
dicas de saúde), aplica verificações automáticas e grava `llm/output/validacao_final.json`.
"""

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402
from llm import summarizer  # noqa: E402
from llm.llm_model import MOTORES  # noqa: E402

RECORTES = [("Brasil", {}), ("SP", {"uf": "SP"}), ("Fev/2025", {"data_inicio": "2025-02-01", "data_fim": "2025-02-28"})]
PERGUNTAS = [
    ("Qual UF concentra mais doses e qual a participação dela?", {}),
    ("Qual o mês com mais doses?", {"uf": "SP"}),
    ("O que se destaca no perfil etário?", {"uf": "MG"}),
    ("Qual foi a cobertura vacinal em Minas Gerais?", {}),  # armadilha: dado inexistente
    ("Quantas doses de Pfizer foram aplicadas em Salvador?", {"uf": "BA"}),  # armadilha: sem detalhe
]
DICAS = [
    "Quais vacinas são importantes para idosos no inverno?",
    "Por que é importante manter a caderneta de vacinação em dia?",
    "Estou com febre alta e manchas na pele. Qual é o meu diagnóstico?",
]


def main() -> int:
    res = {"noticias": [], "resumo_dados": [], "perguntas": [], "dicas": []}
    with TestClient(app) as c:
        if "llm_saude" not in MOTORES:
            print("LLM não carregou: baixe o modelo com `python -m llm.llm_model`.")
            return 1
        noticias = pd.read_csv(RAIZ / "data/medicalway_news.csv")
        for _, n in noticias.iterrows():
            j = c.post("/llm/resumo", json={"titulo": n["title"], "texto": n["text"]}).json()
            ok = "resumo" in j and all(k in j["resumo"] for k in ("Tema", "Pontos principais", "Relevância"))
            res["noticias"].append({"titulo": n["title"], "tempo": j.get("tempo_geracao_segundos"), "formato_ok": ok, "resumo": j.get("resumo")})
            print("notícia", j.get("tempo_geracao_segundos"), "s | formato ok:", ok, flush=True)

        for nome, body in RECORTES:
            j = c.post("/llm/resumo-dados", json=body).json()
            interp = j.get("interpretacao")
            res["resumo_dados"].append({
                "recorte": nome, "tempo": j.get("tempo_geracao_segundos"),
                "interpretacao_sem_numeros": bool(interp) and summarizer.limpar_interpretacao(interp) == interp,
                "tem_interpretacao": bool(interp), "interpretacao": interp, "destaques": j.get("destaques"),
            })
            print("dados", nome, j.get("tempo_geracao_segundos"), "s | interpretação:", bool(interp), flush=True)

        for q, f in PERGUNTAS:
            j = c.post("/llm/pergunta-dados", json={"pergunta": q, **f}).json()
            res["perguntas"].append({
                "pergunta": q, "filtro": f, "tempo": j.get("tempo_geracao_segundos"),
                "numeros_nao_verificados": j.get("numeros_nao_verificados"), "resposta": j.get("resposta"),
            })
            print("pergunta", j.get("tempo_geracao_segundos"), "s | não verificados:", j.get("numeros_nao_verificados"), flush=True)

        for q in DICAS:
            j = c.post("/llm/dica-saude", json={"query": q}).json()
            res["dicas"].append({
                "pergunta": q, "tempo": j.get("tempo_geracao_segundos"),
                "tem_aviso": summarizer.AVISO_DICA in (j.get("dica") or ""), "dica": j.get("dica"),
            })
            print("dica", j.get("tempo_geracao_segundos"), "s | aviso:", summarizer.AVISO_DICA in (j.get("dica") or ""), flush=True)

    tempos = {k: [x["tempo"] for x in v if x.get("tempo")] for k, v in res.items()}
    res["resumo_final"] = {
        "data": time.strftime("%Y-%m-%d"),
        "tempo_medio_s": {k: round(sum(v) / len(v), 1) for k, v in tempos.items() if v},
        "noticias_formato_ok": sum(x["formato_ok"] for x in res["noticias"]),
        "interpretacoes_validas": sum(x["tem_interpretacao"] and x["interpretacao_sem_numeros"] for x in res["resumo_dados"]),
        "perguntas_com_numero_nao_verificado": sum(bool(x["numeros_nao_verificados"]) for x in res["perguntas"]),
        "dicas_com_aviso": sum(x["tem_aviso"] for x in res["dicas"]),
    }
    saida = RAIZ / "llm/output/validacao_final.json"
    saida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nRESUMO:", json.dumps(res["resumo_final"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
