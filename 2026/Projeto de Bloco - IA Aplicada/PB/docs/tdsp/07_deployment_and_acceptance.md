# Deployment Report e Customer Acceptance

> Artefato TDSP · fases **Deployment** e **Customer Acceptance** (substitui a descrição curta do Q2).

## 1. Arquitetura implantada

| Aplicação | Tecnologia | Entrada | Função |
|---|---|---|---|
| Dashboard | Streamlit (`app.py`) | `streamlit run app.py` | Notícias, Vacinas, Base de dados |
| API REST | FastAPI (`api/main.py`) | `uvicorn api.main:app` | Consulta de vacinas + rota de IA |
| Serviço de IA | Transformers (`llm/llm_model.py`) | Carregado no `lifespan` da API | Geração de texto local |

As duas aplicações são independentes e compartilham `src/data_loader.py` e a base processada. Se a LLM falhar no startup, a API de vacinas continua disponível e a rota de IA responde 503.

## 1.1 Dashboard final — página "Ciclo de Dados e IA"

Página inicial do Streamlit (`src/pages/ciclo.py`). Um fluxograma mostra as 5 etapas e quatro abas as detalham; o recorte (UF e mês) vale para as abas 3 e 4.

| Aba | O que mostra | Origem dos números |
|---|---|---|
| 1 · Coleta | Métricas da base, tabela de fontes e métodos, amostra dos dados e as notícias raspadas (com link) | Base processada e scraping |
| 2 · Preparação | Etapas de limpeza, qualidade medida ao vivo (nulos, duplicatas, idade máxima), comparação antes/depois e gráficos de doses por mês e por faixa etária | Cálculo ao vivo + valores de 23/11/2026 (docs/tdsp/04) |
| 3 · IA aplicada | Insights do recorte (mês de pico, UF líder, % de menores de 12 e de 60+), 4 gráficos, resumo executivo por template, botão "Gerar interpretação com IA" e resumo de notícia por IA | Python (números) + LLM (texto) |
| 4 · Pergunte à IA | Chat com perguntas sugeridas; contexto enviado à IA visível; aviso quando a resposta cita números ausentes do contexto | Resumo numérico do recorte + LLM |

Barra lateral: indicador de estado da API de IA (online/offline, modelo carregado). Se a API estiver fora do ar, as abas 1 e 2 e os gráficos continuam funcionando, e os botões de IA exibem uma mensagem clara.

## 1.2 Testes e validação
```bash
python -m unittest discover -s tests -t .   # 31 testes (LLM simulada)
python scripts/validar_llm.py               # ponta a ponta com a LLM real (requer o modelo baixado e ~6 min)
```
Detalhes e resultados em `06_evaluation_report.md` §3.5. A apresentação final está em `08_apresentacao_e_argumentacao.md` e `docs/apresentacao/apresentacao.html` (setas do teclado navegam; imprime um slide por página).

## 2. Estrutura de diretórios atual

```
PB/
├── app.py                      # Dashboard Streamlit (navegação)
├── requirements.txt
├── .env                        # API_VACINACAO, API_NOTICIA (não versionado)
├── api/                        # main.py, route.py, model.py
├── llm/                        # llm_model.py, summarizer.py, llm.md, output/historico.jsonl
├── models/                     # pesos do Qwen (download local)
├── src/                        # ingesting, scraping, preprocessing, data_loader, utils
│   ├── insights.py, llm_client.py  # indicadores, destaques e séries dos gráficos
│   ├── components/news_card.py
│   └── pages/ ciclo.py, noticias.py, vacinas.py, dados.py
├── data/
│   ├── raw/                    # (vazio)
│   ├── processed/              # processed_data.csv
│   └── medicalway_news.csv     # fallback de notícias
└── docs/tdsp/                  # artefatos TDSP (este diretório)
```

## 3. Como executar
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m llm.llm_model          # baixa o modelo (uma vez)
streamlit run app.py             # dashboard
uvicorn api.main:app --reload    # API (docs em /docs) — necessária para os botões de IA
```
Os botões "Resumir com IA" e "Gerar resumo dos dados filtrados" chamam a API (`API_LLM_URL`, padrão `http://localhost:8000`).

## 4. Contratos da API

| Método | Rota | Função | Respostas |
|---|---|---|---|
| GET | `/vacinas` | Consulta com `data_inicio`, `data_fim`, `uf`, `municipio`, `limite` | 200, 400, 422, 503 |
| POST | `/vacinas/consulta` | Mesma consulta por JSON | 200, 400, 422, 503 |
| POST | `/llm/resumo` | `titulo`, `texto`, `max_tokens` → `resumo`, `blocos_processados`, `tempo_geracao_segundos` | 200, 400, 422, 503 |
| POST | `/llm/resumo-dados` | filtros (`uf`, `municipio`, `data_inicio`, `data_fim`) ou `destaques`+`indicadores` prontos → `resumo` (template + interpretação), `destaques`, `interpretacao`, `indicadores`, `total_registros` | 200, 400, 422, 503 |
| POST | `/llm/pergunta-dados` | `pergunta` + filtros (ou `destaques`) → `resposta`, `contexto`, `numeros_nao_verificados`, `tempo_geracao_segundos` | 200, 400, 422, 503 |
| GET | `/llm/status` | → `pronto`, `modelo` (usado pelo dashboard para exibir o estado da IA) | 200 |
| POST | `/llm/dica-saude` | `query`, `contexto_painel`, `max_tokens` → `dica`, `modelo`, `tempo_geracao_segundos` | 200, 400, 422, 503, 504 |

Erros seguem o modelo `ErrorResponse` (`status`, `codigo_http`, `erro`, `mensagem`).

## 5. Riscos de operação e pontos de atenção
- CORS aberto (`allow_origins=["*"]`) e mensagens de exceção devolvidas ao cliente: adequado para ambiente acadêmico, a restringir em produção.
- A API lê o CSV a cada requisição via `load_data()` (cache só vale no Streamlit); considerar cache em memória.
- A inferência síncrona do LLM bloqueia uma thread; sem fila.
- A rota de IA pode ser lenta em CPU.

## 6. Customer Acceptance

| Critério de aceite (Charter §10) | Estado | Evidência / pendência |
|---|---|---|
| Dados coletados e origem documentada | ✅ | Data Summary Report |
| Base consistente e dicionário | ⚠️ | Dicionário publicado; ressalvas no Data Quality Report |
| Dashboard com filtros e indicadores | ✅ | `ciclo.py`, `vacinas.py`, `dados.py` |
| Dashboard mostra o ciclo completo (coleta → insight) com IA interativa | ✅ | Página "Ciclo de Dados e IA" (§1.1) |
| Endpoints GET/POST | ✅ | `route.py` (testes funcionais a registrar) |
| Notícias | ✅ | `scraping.py` (fallback a corrigir) |
| IA (sumarização) integrada ao dashboard e à base | ✅ (implementação) / ⚠️ (qualidade e latência) | Avaliação real feita: ver Evaluation Report; resumos exigem revisão humana |
| Documentação coerente com o código | ✅ | Esta pasta |

**Aceite do cliente (gestor):** a pergunta "a solução responde ao problema?" tem hoje resposta **parcial**. Entrega visão por UF, período e vacina, mas sem cobertura vacinal e sem análise de IA sobre os números. A validação com um usuário-alvo (roteiro de 3 tarefas: filtrar uma UF, baixar um recorte, fazer uma pergunta à IA) fica registrada como próximo passo.

## 7. Exit Report — próximos passos
1. Qualidade: normalização de fabricantes e acentuação (duplicatas, imputação e outliers já corrigidos).
2. Cobertura temporal e denominador populacional (IBGE) para taxa de cobertura.
3. Memória conversacional (Opção 1) sobre os resumos; RAG simples; verificação automática dos números citados.
4. Indicador de "gargalo" para recuperar o ranking de prioridades do Q1.
5. Testes automatizados da API e do pré-processamento.
6. ~~Remover `data/processed_data.csv` redundante~~ — concluído.
