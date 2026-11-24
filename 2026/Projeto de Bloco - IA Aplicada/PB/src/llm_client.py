"""Cliente HTTP da API de IA (a LLM roda no processo da API, não no Streamlit)."""

import os

import requests

API_LLM_URL = os.getenv("API_LLM_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 300  # a geração local pode levar dezenas de segundos


class LLMError(Exception):
    """Falha ao obter resposta da API de IA, com mensagem legível."""


def status_ia() -> dict:
    """Estado da API de IA: {'online': bool, 'pronto': bool, 'modelo': str|None}."""
    try:
        resp = requests.get(f"{API_LLM_URL}/llm/status", timeout=3)
        resp.raise_for_status()
        dados = resp.json()
        return {"online": True, "pronto": bool(dados.get("pronto")), "modelo": dados.get("modelo")}
    except (requests.exceptions.RequestException, ValueError):
        return {"online": False, "pronto": False, "modelo": None}


def _post(rota: str, payload: dict) -> dict:
    try:
        resp = requests.post(f"{API_LLM_URL}{rota}", json=payload, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        raise LLMError(
            f"Não foi possível conectar à API em {API_LLM_URL}. "
            "Inicie-a com: uvicorn api.main:app"
        ) from e
    except requests.exceptions.Timeout as e:
        raise LLMError("A API demorou demais para responder.") from e

    if resp.status_code != 200:
        try:
            detalhe = resp.json().get("mensagem", resp.text)
        except ValueError:
            detalhe = resp.text
        raise LLMError(f"API retornou {resp.status_code}: {detalhe}")
    return resp.json()


def resumir_noticia(titulo: str, texto: str) -> dict:
    return _post("/llm/resumo", {"titulo": titulo, "texto": texto})


def resumir_dados(destaques: str, indicadores: str | None = None) -> dict:
    return _post("/llm/resumo-dados", {"destaques": destaques, "indicadores": indicadores})


def perguntar_dados(pergunta: str, destaques: str) -> dict:
    return _post("/llm/pergunta-dados", {"pergunta": pergunta, "destaques": destaques})
