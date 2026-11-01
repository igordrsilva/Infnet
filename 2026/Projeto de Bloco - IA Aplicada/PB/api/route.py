import json
from datetime import date

import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from api.model import FiltroVacinas
from src.data_loader import load_data

route = APIRouter()


def consultar_vacinas(filtros: FiltroVacinas):
    df = load_data().copy()

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

    if filtros.data_inicio and data_col in df.columns:
        df[data_col] = pd.to_datetime(df[data_col], errors="coerce")
        df = df[df[data_col].dt.date >= filtros.data_inicio]

    if filtros.data_fim and data_col in df.columns:
        df = df[df[data_col].dt.date <= filtros.data_fim]

    if filtros.uf and uf_col in df.columns:
        df = df[df[uf_col].astype(str).str.upper() == filtros.uf.upper()]

    if filtros.municipio and municipio_col in df.columns:
        df = df[df[municipio_col].astype(str).str.upper() == filtros.municipio.upper()]

    df = df.head(filtros.limite)

    dados_json = df.to_json(orient="records", date_format="iso", force_ascii=False)

    return JSONResponse(content=json.loads(dados_json))


# Rota GET
@route.get("/vacinas")
def get_vacinas(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    uf: str | None = None,
    municipio: str | None = None,
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


# Rota POST
@route.post("/vacinas/consulta")
def post_consulta_vacinas(filtros: FiltroVacinas):
    return consultar_vacinas(filtros)
