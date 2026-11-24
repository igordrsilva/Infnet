# Data Summary Report — Vacina Brasil

> Artefato TDSP · fase **Data Acquisition & Understanding**. Descreve como os dados coletados por API e web scraping foram integrados e usados ao longo do projeto, até a IA.

## 1. Fontes de dados

| # | Fonte | Natureza | Método | Código | Saída |
|---|---|---|---|---|---|
| 1 | Dados Abertos Saúde (Gov.br) — doses aplicadas PNI | Estruturada (JSON → tabela) | API REST via `requests`, paginada | `src/ingesting.py` (`get_raw_data`) | `data/raw/data.csv` |
| 2 | Blog Medicalway | Não estruturada (texto HTML) | Web scraping com `requests` + `BeautifulSoup` | `src/scraping.py` (`extract_news`) | `data/medicalway_news.csv` (cache/fallback) |

As URLs ficam em variáveis de ambiente (`API_VACINACAO`, `API_NOTICIA`, arquivo `.env`, fora do versionamento).

### 1.1 Fonte 1 — API de vacinação
- Chamadas `GET` com `limit=1000` e `offset` incremental até a API devolver lista vazia; registros em `data["doses_aplicadas_pni"]`.
- Cabeçalhos `User-Agent` e `Accept: application/json`; timeout de 30 s; tratamento de `ConnectionError`, `HTTPError` e exceções genéricas (a coleta é interrompida e salva o que já obteve).
- Limitação: a mensagem de erro cita "ano 2025" fixo; a API não é filtrada por ano no código. A base resultante cobre 01/01 a 11/06/2025.

### 1.2 Fonte 2 — Notícias (scraping)
- Página-índice do blog: seleção de `a.ct-link-button` com texto "LEIA MAIS", restrita ao mesmo domínio, URL normalizada, sem duplicatas, limite `MAX_NEWS = 5`.
- Para cada link: título (`h1`) e corpo (`.entry-content`, `.post-content`, etc., com *fallback* para `main`/`body`), removendo `script, style, nav, header, footer, aside, form, iframe`; texto de `p, h2, h3, li`.
- Resultado: 5 notícias (título, URL, texto de ~37 mil caracteres cada).
- **Selenium:** previsto no planejamento (Q2/Q3), mas não utilizado, pois o conteúdo é HTML estático. Fica como contingência.

## 2. Fluxo de dados ponta a ponta

```
API PNI ──requests (paginação)──► data/raw/data.csv ─┐
                                                      ├─► preprocessing.py ─► data/processed/processed_data.csv
Blog ──requests+BS4──► lista de notícias ─► CSV fallback                          │
        │                                                                          ├─► Streamlit: Vacinas (indicadores/gráficos)
        └──────────────► Streamlit: Notícias                                       ├─► Streamlit: Base de dados (filtro/download)
                                                                                   ├─► FastAPI: GET /vacinas, POST /vacinas/consulta
                                                                                   ├─► Destaques por template (Python) + interpretação da LLM ─► POST /llm/resumo-dados
                                                                                   ├─► Notícias ─► LLM (map-reduce) ─► POST /llm/resumo
                                                                                   └─► Contexto (filtros) ─► LLM ─► POST /llm/dica-saude
```

Orquestração: `src/data_loader.py`. `load_data()` (com `@st.cache_data`) verifica se existe o processado; se não, usa o bruto; se também não existir, chama a API. `load_news()` raspa o blog e, se falhar, lê o CSV.

## 3. Integração e uso por componente

| Componente | Dados usados | Uso |
|---|---|---|
| Página **Vacinas** | `processed_data.csv` | Filtros (período, UF, município, vacina = fabricante); métricas (doses, UFs, municípios, vacinas); gráficos temporal, por UF e por vacina/fabricante (top 15) |
| Página **Base de dados** | `processed_data.csv` | Tabela filtrada, download CSV, upload de CSV para pré-visualização |
| Página **Notícias** | Scraping / CSV | Cards com resumo (300 caracteres) e link |
| **API** `/vacinas` | `processed_data.csv` via `load_data()` | Consulta com filtros por data, UF, município e limite (máx. 1.000) |
| **API** `/llm/dica-saude` | Pergunta + `contexto_painel` (texto dos filtros) | Prompt para o LLM; resposta com tempo de geração |
| **IA (LLM)** | Notícias raspadas; indicadores agregados da base filtrada; contexto textual dos filtros | Sumarização executiva e dicas de saúde (ver §6) |

## 4. Perfil dos dados (base processada)

| Métrica | Valor |
|---|---|
| Linhas × colunas | 223.625 × 19 (após remover duplicatas e idades > 110; antes 225.958) |
| Período | 01/01/2025 a 11/06/2025 |
| Distribuição mensal | jan 76.983 · fev 32.999 · abr 6 · mai 115.967 · jun 3 (mar: sem registros) |
| UFs (estabelecimento) | 27 |
| Municípios (estabelecimento) | 5.224 |
| Códigos de vacina | 77 |
| Valores distintos de fabricante | 3.014 (grafias heterogêneas) |
| Sexo | F 123.241 · M 102.699 · I 18 |
| Idade | máx. 108 após remoção de outliers (> 110) |
| UFs mais frequentes | SP 48.164 · MG 26.491 · RJ 15.576 · PR 13.869 · BA 12.250 |
| Duplicatas exatas | 0 (2.330 removidas) |
| Notícias | 5 (5 URLs únicas) |

Observações-chave:
- A **amostra é irregular no tempo** (jan, fev e mai concentram 99,9%); séries temporais devem ser lidas com cautela.
- O volume por UF reflete população e registro; **não é cobertura vacinal** (não há denominador).
- Colunas sensíveis foram removidas no pré-processamento (`codigo_paciente`, CEP, estabelecimento identificável, etc.).

## 5. Transformações aplicadas (`src/preprocessing.py`)

1. **`drop_unnecessary_columns`**: remove 33 colunas (códigos técnicos, identificadores, dados do estabelecimento e do sistema de origem).
2. **`fill_missing_values`**: preenche país (Brasil), etnia ("NÃO INDÍGENA"), UF/município do paciente a partir do estabelecimento; tenta imputar moda em tipo de estabelecimento, local de aplicação, fabricante e condição maternal; `dropna`.
3. **`normalize_values`**: capitalização (`str.title`) e unificação de fabricantes por palavra-chave (AstraZeneca, Coronavac, Janssen, Pfizer, Moderna, Butantan, Fiocruz).
4. **`remove_duplicates_and_outliers`**: remove duplicatas e idades fora de 0–110.
5. **`export_processed_data`**: grava `data/processed/processed_data.csv`.

Etapas adicionadas na correção: imputação por moda via `_fill_with_mode` (a versão com `fillna(lambda…)` não funcionava), "Não informado" para condição maternal e `remove_duplicates_and_outliers` (duplicatas e idade fora de 0–110). Pendência (*Data Quality Report*): fabricantes ainda com variações ("Fiocruz" e "Fundacao Oswaldo Cruz", "Serum"…).

## 6. Do dado ao insight por IA

1. **Coleta:** API e scraping alimentam as bases bruta e de notícias.
2. **Transformação:** o pré-processamento gera a base processada.
3. **Exploração:** indicadores e gráficos no Streamlit/API mostram o recorte.
4. **Contextualização:** os filtros ativos (UF, município, período) viram o `contexto_painel`.
5. **Prompt:** `system_prompt` de especialista + contexto + pergunta do usuário (`chat_template` do Qwen).
6. **Geração:** LLM local (`Qwen2.5-3B-Instruct`) devolve a resposta e o tempo de inferência.
7. **Insight:** o gestor recebe interpretação em linguagem natural, com aviso de responsabilidade.

**Caminho de IA implementado (sumarização, Opção 2):**
- *Notícias:* texto raspado → blocos de ~6.000 caracteres → resumo por bloco → resumo executivo (`POST /llm/resumo`).
- *Dados:* base filtrada → `build_highlights` (template Python: panorama, mês de pico, top UFs/municípios, fabricantes, faixa etária, meses fracos) → a LLM escreve só um parágrafo de interpretação **sem algarismos**, filtrado por código (`POST /llm/resumo-dados`).
- Entradas e saídas ficam em `llm/output/historico.jsonl`.
- A LLM não lê o CSV: recebe o resumo numérico calculado em Python e devolve apenas texto interpretativo; os números exibidos nunca vêm da IA.

## 7. Reprodutibilidade
- Dependências em `requirements.txt` (pandas, requests, beautifulsoup4, selenium, streamlit, fastapi, torch, transformers, huggingface_hub).
- Segredos em `.env` (não versionado).
- Modelo baixado com `python -m llm.llm_model` para `models/Qwen2.5-3B-Instruct`.
- Execução: `streamlit run app.py` (dashboard) e `uvicorn api.main:app` (API).
- Observação: `data/raw/` está vazio no repositório atual, a cópia redundante `data/processed_data.csv` foi removida.
