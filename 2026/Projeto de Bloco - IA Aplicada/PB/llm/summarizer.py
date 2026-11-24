"""Prompts, divisão de texto e registro das interações de sumarização (Opção 2).

Este módulo não depende de torch/transformers, o que facilita testá-lo isoladamente.
"""

import json
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
HISTORICO_PATH = OUTPUT_DIR / "historico.jsonl"

# Texto longo é dividido em blocos; só os primeiros são resumidos (limite de custo/latência).
CHUNK_CHARS = 6000
MAX_CHARS_PADRAO = 12000

TEMPERATURA_RESUMO = 0.2  # baixa: resumos devem ser fiéis ao texto

PROMPT_SISTEMA_NOTICIA = (
    "Você é um analista de comunicação em saúde pública no Brasil. "
    "Resuma o texto fornecido em português do Brasil, de forma objetiva e fiel. "
    "Use APENAS informações presentes no texto; não invente dados, números ou fontes. "
    "Se o texto não trouxer algo, não mencione."
)

PROMPT_BLOCO = (
    "Resuma o trecho abaixo em até 4 frases curtas, preservando fatos e números.\n\n"
    "Título do artigo: {titulo}\n\nTrecho:\n{texto}"
)

PROMPT_FINAL_NOTICIA = (
    "Com base no conteúdo abaixo, escreva um RESUMO EXECUTIVO no formato:\n"
    "**Tema:** uma frase.\n"
    "**Pontos principais:** 3 tópicos curtos.\n"
    "**Relevância para a gestão em saúde:** 1 frase.\n\n"
    "Título do artigo: {titulo}\n\nConteúdo:\n{texto}"
)

PROMPT_SISTEMA_DADOS = (
    "Você é um analista de saúde pública no Brasil apoiando gestores do SUS. "
    "Você receberá um resumo numérico já calculado. Escreva UM parágrafo de interpretação "
    "(até 4 frases) em português do Brasil. "
    "Regras: (1) NÃO escreva nenhum número, percentual, data ou ano; o leitor já vê os números ao lado. "
    "(2) Use só o que está no resumo; não invente causas, comparações ou recomendações clínicas. "
    "(3) Não critique o tamanho do recorte. "
    "(4) Aponte padrões (concentração, irregularidade ao longo do tempo, perfil etário) e sugira "
    "que o gestor verifique as lacunas indicadas."
)

PROMPT_FINAL_DADOS = (
    "Resumo numérico:\n{destaques}\n\n"
    "Escreva o parágrafo de interpretação, sem números."
)


PROMPT_SISTEMA_PERGUNTA = (
    "Você é um analista de saúde pública no Brasil apoiando gestores do SUS. "
    "Responda à pergunta do usuário usando SOMENTE o resumo numérico fornecido. "
    "Regras: (1) copie números exatamente como aparecem no resumo; nunca calcule, estime ou invente valores. "
    "(2) Se o resumo não contiver a resposta, diga claramente que os dados do recorte atual não permitem "
    "responder e sugira ajustar o recorte (UF, mês) no painel. "
    "(3) Os dados são registros de doses aplicadas, sem população-alvo: não afirme cobertura vacinal, "
    "causas ou recomendações clínicas. (4) Responda em português do Brasil, em até 4 frases curtas."
)

PROMPT_PERGUNTA = (
    "Resumo numérico do recorte atual:\n{destaques}\n\n"
    "Pergunta do usuário: {pergunta}"
)


def _canonico(numero: str) -> str:
    return "".join(c for c in numero if c.isdigit())


def numeros_nao_verificados(resposta: str, referencia: str) -> list[str]:
    """Números da resposta que não aparecem na referência (comparação só pelos dígitos).

    Ignora números de 1 dígito (marcadores de lista). Serve para sinalizar possível invenção.
    """
    refs = {_canonico(n) for n in re.findall(r"\d[\d.,/]*\d|\d", referencia)}
    achados = re.findall(r"\d[\d.,/]*\d|\d", resposta)
    return sorted({n for n in achados if len(_canonico(n)) > 1 and _canonico(n) not in refs})


AVISO_DICA = "Aviso: estas informações são educativas e não substituem consulta médica ou atendimento no SUS."


def finalizar_dica(texto: str) -> str:
    """Remove o trecho final cortado pelo limite de tokens e acrescenta o aviso de responsabilidade.

    O aviso é adicionado por código (não depende de o modelo lembrar de escrevê-lo).
    """
    texto = texto.strip()
    if texto and texto[-1] not in ".!?":
        corte = max(texto.rfind("."), texto.rfind("!"), texto.rfind("?"))
        if corte > len(texto) // 2:
            texto = texto[: corte + 1]
    return f"{texto}\n\n{AVISO_DICA}"


def limpar_interpretacao(texto: str) -> str:
    """Mantém só frases completas e sem dígitos (a interpretação não pode conter números).

    Descarta a frase final cortada pelo limite de tokens e qualquer frase com algarismos.
    Retorna string vazia se nada restar.
    """
    frases = re.findall(r"[^.!?]+[.!?]", " ".join(texto.split()))
    return " ".join(f.strip() for f in frases if not any(c.isdigit() for c in f))


def chunk_text(text: str, chunk_chars: int = CHUNK_CHARS, max_chars: int = MAX_CHARS_PADRAO) -> list[str]:
    """Trunca o texto em ``max_chars`` e divide em blocos de ~``chunk_chars``, cortando em fim de linha/frase."""
    text = (text or "").strip()[:max_chars]
    chunks: list[str] = []
    while text:
        if len(text) <= chunk_chars:
            chunks.append(text)
            break
        corte = max(text.rfind("\n", 0, chunk_chars), text.rfind(". ", 0, chunk_chars))
        if corte < chunk_chars // 2:  # sem ponto de corte razoável
            corte = chunk_chars
        else:
            corte += 1
        chunks.append(text[:corte].strip())
        text = text[corte:].strip()
    if len(chunks) > 1 and len(chunks[-1]) < 500:  # evita bloco final minúsculo
        chunks[-2] += "\n" + chunks.pop()
    return chunks


def registrar_interacao(tipo: str, entrada: dict, saida: str, tempo_segundos: float, modelo: str) -> None:
    """Acrescenta a interação em ``llm/output/historico.jsonl``. Falhas de escrita não derrubam a API."""
    registro = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tipo": tipo,
        "modelo": modelo,
        "tempo_segundos": tempo_segundos,
        "entrada": entrada,
        "saida": saida,
    }
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with HISTORICO_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"Aviso: não foi possível gravar o histórico da LLM: {e}")
