import json
from datetime import date

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from api.model import (
    ErrorResponse,
    FiltroVacinas,
    HealthTipRequest,
    HealthTipResponse,
    PerguntaDadosRequest,
    PerguntaDadosResponse,
    ResumoDadosRequest,
    ResumoNoticiaRequest,
    ResumoResponse,
    VacinasConsultaResponse,
)
from llm.llm_model import MODEL_ID, MOTORES
from llm import summarizer
from src.data_loader import load_data
from src.insights import build_data_context, build_highlights

route = APIRouter()


def _carregar_base() -> pd.DataFrame:
    """Carrega a base de vacinação, traduzindo falhas em HTTPException."""
    try:
        df = load_data().copy()
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Base de dados de vacinação indisponível no momento: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar a base de dados de vacinação: {str(e)}"
        )
    if df.empty:
        raise HTTPException(
            status_code=503,
            detail="A base de dados de vacinação está vazia ou não pôde ser lida."
        )
    return df


def _filtrar_base(df: pd.DataFrame, filtros) -> pd.DataFrame:
    """Aplica data_inicio, data_fim, uf e municipio (qualquer objeto com esses atributos)."""
    data_col = "data_vacina"
    uf_col = (
        "sigla_uf_estabelecimento"
        if "sigla_uf_estabelecimento" in df.columns
        else "sigla_uf_paciente"
    )
    municipio_col = (
        "nome_municipio_estabelecimento"
        if "nome_municipio_estabelecimento" in df.columns
        else "nome_municipio_paciente"
    )

    if (filtros.data_inicio or filtros.data_fim) and data_col in df.columns:
        df[data_col] = pd.to_datetime(df[data_col], errors="coerce")
        if filtros.data_inicio:
            df = df[df[data_col].dt.date >= filtros.data_inicio]
        if filtros.data_fim:
            df = df[df[data_col].dt.date <= filtros.data_fim]

    if filtros.uf and uf_col in df.columns:
        df = df[df[uf_col].astype(str).str.upper() == filtros.uf.strip().upper()]

    if filtros.municipio and municipio_col in df.columns:
        df = df[df[municipio_col].astype(str).str.upper() == filtros.municipio.strip().upper()]

    return df


def consultar_vacinas(filtros: FiltroVacinas) -> VacinasConsultaResponse:
    if filtros.data_inicio and filtros.data_fim and filtros.data_inicio > filtros.data_fim:
        raise HTTPException(
            status_code=400,
            detail="A 'data_inicio' não pode ser posterior à 'data_fim'."
        )

    df = _carregar_base()

    try:
        df = _filtrar_base(df, filtros)
        df = df.head(filtros.limite)
        registros = json.loads(df.to_json(orient="records", date_format="iso", force_ascii=False))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar e filtrar os dados de vacinação: {str(e)}"
        )

    return VacinasConsultaResponse(
        status="sucesso",
        total_registros=len(registros),
        filtros_aplicados=filtros.model_dump(exclude_none=True),
        dados=registros,
    )


# Rota GET com Response Model validado
@route.get(
    "/vacinas",
    response_model=VacinasConsultaResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Parâmetros de filtro inválidos"},
        503: {"model": ErrorResponse, "description": "Base de dados indisponível"},
    },
    tags=["Vacinação"],
)
def get_vacinas(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    municipio: str | None = Query(default=None, min_length=2),
    limite: int = Query(default=100, ge=1, le=1000),
):
    filtros = FiltroVacinas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        uf=uf,
        municipio=municipio,
        limite=limite,
    )
    return consultar_vacinas(filtros)


# Rota POST com Response Model validado
@route.post(
    "/vacinas/consulta",
    response_model=VacinasConsultaResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Parâmetros de filtro inválidos"},
        503: {"model": ErrorResponse, "description": "Base de dados indisponível"},
    },
    tags=["Vacinação"],
)
def post_consulta_vacinas(filtros: FiltroVacinas):
    return consultar_vacinas(filtros)


# Rota POST para geração de dicas de saúde com a LLM local
@route.post(
    "/llm/dica-saude",
    response_model=HealthTipResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Prompt ou dados textuais inválidos"},
        503: {"model": ErrorResponse, "description": "Modelo LLM não carregado ou indisponível"},
        504: {"model": ErrorResponse, "description": "Tempo limite de geração excedido"},
        500: {"model": ErrorResponse, "description": "Falha interna durante a inferência"},
    },
    tags=["Inteligência Artificial - Saúde"],
)
def post_dica_saude(payload: HealthTipRequest):
    llm_service = MOTORES.get("llm_saude")

    if llm_service is None or not llm_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail=(
                "O serviço de IA (modelo LLM local) está temporariamente indisponível ou não foi "
                "carregado na inicialização do servidor. Verifique os logs da API."
            ),
        )

    try:
        resposta, tempo_geracao = llm_service.generate_health_tip(
            user_input=payload.query,
            context=payload.contexto_painel or "",
            max_new_tokens=payload.max_tokens,
        )
        return HealthTipResponse(
            status="sucesso",
            dica=summarizer.finalizar_dica(resposta),
            modelo=MODEL_ID,
            tempo_geracao_segundos=tempo_geracao,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível processar o texto enviado: {str(e)}",
        )
    except TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail=f"A geração da resposta excedeu o tempo limite permitido: {str(e)}",
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"O motor da LLM encontrou uma indisponibilidade durante a execução: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno inesperado ao gerar dica de saúde localmente: {str(e)}",
        )

# ---------------------------------------------------------------------------
# Sumarização com LLM (notícias e dados)
# ---------------------------------------------------------------------------
_RESPOSTAS_LLM = {
    400: {"model": ErrorResponse, "description": "Entrada inválida"},
    503: {"model": ErrorResponse, "description": "Modelo LLM ou base de dados indisponível"},
    500: {"model": ErrorResponse, "description": "Falha interna durante a inferência"},
}


def _obter_llm():
    llm_service = MOTORES.get("llm_saude")
    if llm_service is None or not llm_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail=(
                "O serviço de IA (modelo LLM local) está temporariamente indisponível ou não foi "
                "carregado na inicialização do servidor. Verifique os logs da API."
            ),
        )
    return llm_service


def _executar_llm(funcao):
    """Executa uma chamada à LLM traduzindo exceções em HTTPException."""
    try:
        return funcao()
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Não foi possível processar o texto enviado: {str(e)}")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"O motor da LLM encontrou uma indisponibilidade: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno inesperado ao gerar o resumo: {str(e)}")


@route.post(
    "/llm/resumo",
    response_model=ResumoResponse,
    responses=_RESPOSTAS_LLM,
    tags=["Inteligência Artificial - Saúde"],
)
def post_resumo_noticia(payload: ResumoNoticiaRequest):
    """Resume um texto (ex.: notícia extraída por scraping) em formato executivo."""
    llm_service = _obter_llm()
    resumo, tempo, blocos = _executar_llm(
        lambda: llm_service.summarize_news(
            titulo=payload.titulo,
            texto=payload.texto,
            max_new_tokens=payload.max_tokens,
        )
    )
    summarizer.registrar_interacao(
        tipo="resumo_noticia",
        entrada={"titulo": payload.titulo, "caracteres": len(payload.texto), "blocos": blocos},
        saida=resumo,
        tempo_segundos=tempo,
        modelo=MODEL_ID,
    )
    return ResumoResponse(
        resumo=resumo,
        modelo=MODEL_ID,
        tempo_geracao_segundos=tempo,
        blocos_processados=blocos,
    )


@route.post(
    "/llm/resumo-dados",
    response_model=ResumoResponse,
    responses=_RESPOSTAS_LLM,
    tags=["Inteligência Artificial - Saúde"],
)
def post_resumo_dados(payload: ResumoDadosRequest):
    """Resumo executivo dos dados: números calculados em Python; a LLM só escreve a interpretação (sem números)."""
    if payload.data_inicio and payload.data_fim and payload.data_inicio > payload.data_fim:
        raise HTTPException(
            status_code=400,
            detail="A 'data_inicio' não pode ser posterior à 'data_fim'."
        )

    llm_service = _obter_llm()
    filtros_txt = ", ".join(
        f"{k}={v}"
        for k, v in payload.model_dump(
            exclude={"max_tokens", "indicadores", "destaques"}, exclude_none=True
        ).items()
    )
    total_registros = None

    if payload.destaques and payload.destaques.strip():
        destaques = payload.destaques.strip()
        indicadores = (payload.indicadores or "").strip() or None
    else:
        df = _carregar_base()
        try:
            df = _filtrar_base(df, payload)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar e filtrar os dados de vacinação: {str(e)}"
            )
        if df.empty:
            raise HTTPException(status_code=400, detail="Nenhum registro encontrado para os filtros informados.")
        destaques = build_highlights(df, filtros_txt)
        indicadores = build_data_context(df, filtros_txt)
        total_registros = len(df)

    interpretacao, tempo = _executar_llm(
        lambda: llm_service.interpret_data(destaques, max_new_tokens=payload.max_tokens)
    )
    resumo = destaques
    if interpretacao:
        resumo += f"\n\n**Interpretação (IA):** {interpretacao}"

    summarizer.registrar_interacao(
        tipo="resumo_dados",
        entrada={"filtros": filtros_txt, "destaques": destaques},
        saida=interpretacao or "(interpretação descartada: o modelo citou números)",
        tempo_segundos=tempo,
        modelo=MODEL_ID,
    )
    return ResumoResponse(
        resumo=resumo,
        modelo=MODEL_ID,
        tempo_geracao_segundos=tempo,
        indicadores=indicadores,
        destaques=destaques,
        interpretacao=interpretacao,
        total_registros=total_registros,
    )


@route.get("/llm/status", tags=["Inteligência Artificial - Saúde"])
def get_llm_status():
    """Informa se o modelo local está carregado (usado pelo dashboard)."""
    servico = MOTORES.get("llm_saude")
    return {"pronto": bool(servico is not None and servico.is_ready()), "modelo": MODEL_ID}


@route.post(
    "/llm/pergunta-dados",
    response_model=PerguntaDadosResponse,
    responses=_RESPOSTAS_LLM,
    tags=["Inteligência Artificial - Saúde"],
)
def post_pergunta_dados(payload: PerguntaDadosRequest):
    """Responde a uma pergunta do gestor com base no resumo numérico do recorte; verifica os números citados."""
    if payload.data_inicio and payload.data_fim and payload.data_inicio > payload.data_fim:
        raise HTTPException(status_code=400, detail="A 'data_inicio' não pode ser posterior à 'data_fim'.")

    llm_service = _obter_llm()

    if payload.destaques and payload.destaques.strip():
        contexto = payload.destaques.strip()
    else:
        df = _carregar_base()
        try:
            df = _filtrar_base(df, payload)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar e filtrar os dados de vacinação: {str(e)}"
            )
        if df.empty:
            raise HTTPException(status_code=400, detail="Nenhum registro encontrado para os filtros informados.")
        filtros_txt = ", ".join(
            f"{k}={v}"
            for k, v in payload.model_dump(
                exclude={"pergunta", "max_tokens", "destaques"}, exclude_none=True
            ).items()
        )
        contexto = build_highlights(df, filtros_txt)

    resposta, tempo = _executar_llm(
        lambda: llm_service.answer_question(payload.pergunta, contexto, max_new_tokens=payload.max_tokens)
    )
    fora = summarizer.numeros_nao_verificados(resposta, contexto + " " + payload.pergunta)

    summarizer.registrar_interacao(
        tipo="pergunta_dados",
        entrada={"pergunta": payload.pergunta, "contexto": contexto},
        saida=resposta,
        tempo_segundos=tempo,
        modelo=MODEL_ID,
    )
    return PerguntaDadosResponse(
        resposta=resposta,
        modelo=MODEL_ID,
        tempo_geracao_segundos=tempo,
        contexto=contexto,
        numeros_nao_verificados=fora,
    )
