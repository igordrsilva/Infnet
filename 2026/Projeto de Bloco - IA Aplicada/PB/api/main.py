from fastapi import FastAPI

from api.route import route as vacina_routes

app = FastAPI(
    title="API de Vacinação",
    description="API para consulta de dados de vacinação no Brasil",
    version="1.0.0",
)
app.include_router(vacina_routes)
