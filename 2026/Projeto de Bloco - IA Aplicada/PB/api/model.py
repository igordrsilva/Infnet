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


class ResumoNoticiaRequest(BaseModel):
    titulo: str = Field(default="", max_length=300, description="Título do texto (opcional).")
    texto: str = Field(..., min_length=50, max_length=200000, description="Texto a ser resumido.")
    max_tokens: int = Field(default=250, ge=50, le=600, description="Limite de tokens do resumo.")


class ResumoDadosRequest(BaseModel):
    data_inicio: date | None = Field(default=None, description="Data inicial do filtro (YYYY-MM-DD).")
    data_fim: date | None = Field(default=None, description="Data final do filtro (YYYY-MM-DD).")
    uf: str | None = Field(default=None, min_length=2, max_length=2, description="Sigla da UF (ex: RS, SP).")
    municipio: str | None = Field(default=None, min_length=2, description="Nome do município.")
    indicadores: str | None = Field(
        default=None,
        max_length=4000,
        description="Indicadores já calculados (ex.: pelo dashboard, com filtros múltiplos). "
                    "Se informado, a API não consulta a base.",
    )
    destaques: str | None = Field(
        default=None,
        max_length=4000,
        description="Destaques determinísticos já calculados (ver `build_highlights`). "
                    "Se informado junto com `indicadores`, a API não consulta a base.",
    )
    max_tokens: int = Field(default=200, ge=50, le=600, description="Limite de tokens da interpretação.")


class PerguntaDadosRequest(BaseModel):
    pergunta: str = Field(..., min_length=3, max_length=500, description="Pergunta sobre os dados do recorte.")
    data_inicio: date | None = Field(default=None, description="Data inicial do filtro (YYYY-MM-DD).")
    data_fim: date | None = Field(default=None, description="Data final do filtro (YYYY-MM-DD).")
    uf: str | None = Field(default=None, min_length=2, max_length=2, description="Sigla da UF (ex: RS, SP).")
    municipio: str | None = Field(default=None, min_length=2, description="Nome do município.")
    destaques: str | None = Field(
        default=None, max_length=4000, description="Resumo numérico já calculado; evita consultar a base."
    )
    max_tokens: int = Field(default=200, ge=50, le=600, description="Limite de tokens da resposta.")


class PerguntaDadosResponse(BaseModel):
    status: str = Field(default="sucesso")
    resposta: str = Field(..., description="Resposta da LLM, ancorada no resumo numérico.")
    modelo: str = Field(default="Qwen/Qwen2.5-3B-Instruct")
    tempo_geracao_segundos: float = Field(..., ge=0)
    contexto: str = Field(..., description="Resumo numérico enviado à LLM como contexto.")
    numeros_nao_verificados: list[str] = Field(
        default_factory=list,
        description="Números da resposta ausentes do contexto (possível invenção).",
    )


class ResumoResponse(BaseModel):
    """Resposta das rotas de sumarização."""
    status: str = Field(default="sucesso")
    resumo: str = Field(..., description="Resumo gerado pelo modelo local.")
    modelo: str = Field(default="Qwen/Qwen2.5-3B-Instruct")
    tempo_geracao_segundos: float = Field(..., ge=0)
    blocos_processados: int | None = Field(default=None, description="Blocos de texto resumidos (notícias).")
    indicadores: str | None = Field(default=None, description="Indicadores detalhados (dados), para transparência.")
    destaques: str | None = Field(default=None, description="Destaques numéricos calculados em Python (sem IA).")
    interpretacao: str | None = Field(
        default=None,
        description="Parágrafo gerado pela LLM, sem números; nulo se o modelo violar a regra.",
    )
    total_registros: int | None = Field(default=None, description="Registros considerados (dados).")


class ErrorResponse(BaseModel):
    """Response Model padronizado para todas as respostas de erro da API."""
    status: str = Field(default="erro", description="Indicador de falha na requisição.")
    codigo_http: int = Field(..., description="Código de status HTTP retornado.")
    erro: str = Field(..., description="Categoria resumida do erro.")
    mensagem: str = Field(..., description="Descrição clara e explicativa para diagnóstico.")