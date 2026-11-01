from datetime import date

from pydantic import BaseModel, Field


class FiltroVacinas(BaseModel):
    data_inicio: date | None = None
    data_fim: date | None = None
    uf: str | None = None
    municipio: str | None = None
    limite: int = Field(default=100, ge=1, le=1000)
