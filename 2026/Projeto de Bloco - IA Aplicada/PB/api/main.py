import gc
from contextlib import asynccontextmanager
import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.model import ErrorResponse
from api.route import route as vacina_routes
from llm.llm_model import MOTORES, carregar_llm


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("🚀 Executando lifespan: iniciando carregamento da LLM...")
    try:
        MOTORES["llm_saude"] = carregar_llm()
        print("✅ LLM registrada em MOTORES com sucesso!")
    except Exception as e:
        # Não derruba a API de vacinas caso a LLM falhe; a rota da LLM responderá com 503
        MOTORES.pop("llm_saude", None)
        print(f"⚠️ AVISO: Falha ao carregar LLM no startup ({str(e)}). A rota /llm retornará 503.")

    yield

    MOTORES.clear()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    elif torch.backends.mps.is_available():
        torch.mps.empty_cache()


app = FastAPI(
    title="API de Vacinação",
    description="API para consulta de dados de vacinação e geração de dicas de saúde no Brasil",
    version="1.0.0",
    lifespan=lifespan,
    responses={
        422: {"model": ErrorResponse, "description": "Erro de validação nos dados enviados"},
        500: {"model": ErrorResponse, "description": "Erro interno inesperado no servidor"},
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    """Padroniza todas as HTTPException no formato ErrorResponse."""
    categorias = {
        400: "Requisição Inválida",
        404: "Recurso Não Encontrado",
        500: "Erro Interno do Servidor",
        503: "Serviço Indisponível",
        504: "Tempo Limite Excedido (Timeout)",
    }
    erro_corpo = ErrorResponse(
        codigo_http=exc.status_code,
        erro=categorias.get(exc.status_code, "Erro na Requisição"),
        mensagem=str(exc.detail),
    )
    return JSONResponse(status_code=exc.status_code, content=erro_corpo.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    """Padroniza erros de validação Pydantic (422) com detalhes legíveis dos campos."""
    detalhes = "; ".join(
        f"Campo '{' -> '.join(str(loc) for loc in err['loc'])}': {err['msg']}"
        for err in exc.errors()
    )
    erro_corpo = ErrorResponse(
        codigo_http=422,
        erro="Dados de Entrada Inválidos",
        mensagem=detalhes,
    )
    return JSONResponse(status_code=422, content=erro_corpo.model_dump())


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    """Captura falhas imprevistas sem vazar stacktraces brutos ao cliente."""
    erro_corpo = ErrorResponse(
        codigo_http=500,
        erro="Erro Interno Inesperado",
        mensagem=f"Ocorreu uma falha interna ao processar a solicitação: {str(exc)}",
    )
    return JSONResponse(status_code=500, content=erro_corpo.model_dump())


app.include_router(vacina_routes)