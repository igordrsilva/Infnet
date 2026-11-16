from datetime import date
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class FiltroVacinas(BaseModel):
    data_inicio: date | None = Field(default=None, description="Data inicial do filtro (YYYY-MM-DD).")
    data_fim: date | None = Field(default=None, description="Data final do filtro (YYYY-MM-DD).")
    uf: str | None = Field(default=None, min_length=2, max_length=2, description="Sigla da UF (ex: RS, SP).")
    municipio: str | None = Field(default=None, min_length=2, description="Nome do município.")
    limite: int = Field(default=100, ge=1, le=1000, description="Quantidade máxima de registros retornados.")


class VacinaItemResponse(BaseModel):
    """Representa um registro individual de vacinação (permite campos dinâmicos da base)."""
    model_config = ConfigDict(extra="allow")

    data_vacina: str | None = Field(default=None, description="Data da aplicação da vacina em formato ISO.")


class VacinasConsultaResponse(BaseModel):
    """Response Model estruturado para as rotas de consulta de vacinas."""
    status: str = Field(default="sucesso", description="Status da operação.")
    total_registros: int = Field(..., ge=0, description="Total de registros retornados na consulta.")
    filtros_aplicados: dict[str, Any] = Field(default_factory=dict, description="Resumo dos filtros utilizados.")
    dados: list[VacinaItemResponse] = Field(default_factory=list, description="Lista de registros de vacinação.")


class HealthTipRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Dúvida ou solicitação de dica de saúde do visitante.",
        examples=["Quais vacinas são importantes para idosos no inverno?"]
    )
    contexto_painel: str | None = Field(
        default=None,
        max_length=1500,
        description="Resumo dos filtros ativos no Streamlit (ex: UF, município ou período)."
    )
    max_tokens: int = Field(
        default=200,
        ge=50,
        le=1024,
        description="Limite máximo de tokens gerados na resposta."
    )

    @field_validator("query")
    @classmethod
    def validar_query_nao_vazia(cls, valor: str) -> str:
        texto_limpo = valor.strip()
        if len(texto_limpo) < 3:
            raise ValueError("A pergunta ('query') deve conter pelo menos 3 caracteres válidos.")
        return texto_limpo


class HealthTipResponse(BaseModel):
    """Response Model estruturado para a rota de dicas de saúde via LLM."""
    status: str = Field(default="sucesso", description="Status da inferência.")
    dica: str = Field(..., description="Dica de saúde gerada pelo modelo local.")
    modelo: str = Field(default="Qwen/Qwen2.5-3B-Instruct", description="Identificador do modelo utilizado.")
    tempo_geracao_segundos: float = Field(..., ge=0, description="Tempo gasto na inferência local em segundos.")


class ErrorResponse(BaseModel):
    """Response Model padronizado para todas as respostas de erro da API."""
    status: str = Field(default="erro", description="Indicador de falha na requisição.")
    codigo_http: int = Field(..., description="Código de status HTTP retornado.")
    erro: str = Field(..., description="Categoria resumida do erro.")
    mensagem: str = Field(..., description="Descrição clara e explicativa para diagnóstico.")