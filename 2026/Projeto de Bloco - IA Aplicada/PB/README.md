# Vacina Brasil — do dado público ao insight com IA

Dashboard e API que coletam dados públicos de vacinação (API Gov.br) e notícias de saúde (web scraping), preparam a base, calculam indicadores e usam uma **LLM local** (`Qwen2.5-3B-Instruct`) para interpretar, resumir e responder perguntas sobre os dados. Projeto de Bloco (Infnet), metodologia **TDSP**, alinhado ao **ODS 3 — Saúde e Bem-Estar**.

## Execução rápida

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # preencha API_VACINACAO e API_NOTICIA
python -m llm.llm_model           # baixa o modelo (~6 GB, uma vez)
uvicorn api.main:app --port 8000  # API + LLM (terminal 1)
streamlit run app.py              # dashboard (terminal 2)
```

Sem a API de IA, o dashboard continua funcionando (dados, gráficos, notícias); só os botões de IA ficam indisponíveis, e a barra lateral avisa.

## Testes

```bash
python -m unittest discover -s tests -t .   # 31 testes (rápidos, LLM simulada)
python scripts/validar_llm.py               # validação ponta a ponta com a LLM real
```

## Estrutura

```
app.py                  # navegação do Streamlit
api/                    # FastAPI: consulta de dados e rotas de IA
llm/                    # serviço da LLM, prompts (summarizer.py) e llm/output (histórico e avaliações)
src/                    # ingesting, scraping, preprocessing, insights, llm_client, pages/
data/                   # raw/, processed/, medicalway_news.csv
tests/  scripts/        # testes automatizados e validação com LLM real
docs/tdsp/              # artefatos TDSP (charter, data summary, qualidade, modelagem, avaliação, implantação, apresentação)
docs/apresentacao/      # deck da apresentação final (HTML)
```

## Documentação

Comece por [docs/tdsp/README.md](docs/tdsp/README.md). A argumentação da solução está em [docs/tdsp/08_apresentacao_e_argumentacao.md](docs/tdsp/08_apresentacao_e_argumentacao.md).

## API (principais rotas)

| Rota | Função |
|---|---|
| `GET /vacinas`, `POST /vacinas/consulta` | Consulta de registros com filtros |
| `POST /llm/resumo` | Resumo executivo de uma notícia (map-reduce) |
| `POST /llm/resumo-dados` | Destaques numéricos (template) + interpretação da LLM |
| `POST /llm/pergunta-dados` | Pergunta sobre o recorte, com verificação dos números citados |
| `POST /llm/dica-saude` | Dicas de saúde com aviso de responsabilidade |
| `GET /llm/status` | Estado do modelo |

Documentação interativa em `http://localhost:8000/docs`.

## Limitações conhecidas

Os dados cobrem cerca de 5 meses de 2025, de forma irregular, e não trazem população-alvo, então **não é possível calcular cobertura vacinal**. O modelo de 3B pode errar na redação; por isso os números do dashboard são calculados em Python e a IA só interpreta. Detalhes em `docs/tdsp/06_evaluation_report.md`.
