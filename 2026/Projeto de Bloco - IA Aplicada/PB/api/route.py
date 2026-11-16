import json
from datetime import date

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from api.model import (
    ErrorResponse,
    FiltroVacinas,
    HealthTipRequest,
    HealthTipResponse,
    VacinasConsultaResponse,
)
from llm.llm_model import MODEL_ID, MOTORES
from src.data_loader import load_data

route = APIRouter()


def consultar_vacinas(filtros: FiltroVacinas) -> VacinasConsultaResponse:
    if filtros.data_inicio and filtros.data_fim and filtros.data_inicio > filtros.data_fim:
        raise HTTPException(
            status_code=400,
            detail="A 'data_inicio' não pode ser posterior à 'data_fim'."
        )

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

    try:
        if filtros.data_inicio and data_col in df.columns:
            df[data_col] = pd.to_datetime(df[data_col], errors="coerce")
            df = df[df[data_col].dt.date >= filtros.data_inicio]

        if filtros.data_fim and data_col in df.columns:
            df[data_col] = pd.to_datetime(df[data_col], errors="coerce")
            df = df[df[data_col].dt.date <= filtros.data_fim]

        if filtros.uf and uf_col in df.columns:
            df = df[df[uf_col].astype(str).str.upper() == filtros.uf.strip().upper()]

        if filtros.municipio and municipio_col in df.columns:
            df = df[df[municipio_col].astype(str).str.upper() == filtros.municipio.strip().upper()]

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
            dica=resposta,
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