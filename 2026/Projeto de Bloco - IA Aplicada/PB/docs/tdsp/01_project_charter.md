# Project Charter — Vacina Brasil

> Artefato TDSP · fase **Business Understanding** · versão atualizada (substitui o rascunho do Q3).
> Reconcilia o enunciado do Q1 (gargalos da saúde pública) com o escopo efetivamente construído (vacinação, ODS 3).

## 1. Visão geral

| Item | Descrição |
|---|---|
| **Projeto** | Vacina Brasil — Análise e Monitoramento da Vacinação no Brasil |
| **Metodologia** | TDSP (Team Data Science Process) |
| **ODS** | ODS 3 — Saúde e Bem-Estar (meta 3.b: apoio a vacinas e medicamentos; meta 3.8: cobertura universal) |
| **Público-alvo** | Gestores e analistas de planejamento em saúde pública (não o cidadão final) |
| **Tecnologias** | Python, Streamlit (dashboard), FastAPI (API REST), requests + BeautifulSoup (scraping), pandas, Hugging Face Transformers (`Qwen/Qwen2.5-3B-Instruct`, local) |

## 2. Problema de negócio

Os dados públicos de vacinação existem, mas são volumosos (centenas de milhares de registros, dezenas de colunas, múltiplas grafias para o mesmo fabricante/município) e vêm separados das notícias do setor. Isso dificulta que um gestor responda perguntas simples: *onde, quando e com quais vacinas a imunização está concentrada ou ausente?* e *o que está sendo noticiado sobre o tema?*

**Pergunta-guia (refinamento do Q1):** quais UFs, períodos e vacinas concentram a aplicação de doses e onde há lacunas de registro que merecem atenção do gestor? A ordenação de UFs/vacinas por volume e por lacuna é o "ranking de prioridades" que substitui o ranking genérico de "cinco áreas da saúde" do Q1, hoje fora do escopo.

## 3. Objetivos

**Geral:** transformar dados brutos de vacinação (API) e informação textual (notícias) em insights acessíveis, por meio de dashboard, API e assistente de IA generativa.

**Específicos**
1. Coletar dados estruturados via API pública e notícias via web scraping.
2. Limpar, padronizar e documentar a base (raw → processed).
3. Disponibilizar indicadores e filtros por período, UF, município e vacina.
4. Expor os dados por API REST (GET e POST) com contratos validados.
5. Oferecer um assistente de IA (LLM local) que responda perguntas de saúde com contexto dos filtros do painel.
6. Documentar todo o ciclo, da obtenção dos dados ao insight.

## 4. Escopo

**Dentro do escopo**
- Coleta paginada da API de Dados Abertos (doses aplicadas — PNI) e scraping do blog Medicalway.
- Pré-processamento e armazenamento em `data/raw` e `data/processed`.
- Dashboard Streamlit: **Ciclo de Dados e IA** (coleta → preparação → IA aplicada → perguntas à IA), Notícias, Vacinas (indicadores e gráficos), Base de dados (consulta, download, upload).
- API FastAPI: `GET /vacinas`, `POST /vacinas/consulta`, `POST /llm/dica-saude`.
- LLM local com engenharia de prompts: **sumarização automática de notícias e dos indicadores da base** (Opção 2), além de dicas de saúde (system prompt + contexto do painel).

**Fora do escopo (nesta versão)**
- Modelos preditivos/estatísticos de cobertura vacinal (não há denominador populacional na base).
- Ranking multissetorial de áreas da saúde (Q1 original).
- Automação de navegador (Selenium): previsto no Q2/Q3, mas **não foi necessário** — o blog é HTML estático; fica como evolução.
- Memória conversacional e agentes (Opções 1 e 3 do enunciado), com possível evolução futura.

## 5. Stakeholders

| Stakeholder | Interesse | Como é atendido |
|---|---|---|
| Ministério da Saúde | Visão nacional | Indicadores nacionais e comparação entre UFs |
| Secretarias Estaduais | Comparação regional | Filtros por UF e gráfico de doses por UF |
| Secretarias Municipais | Prioridades locais | Filtro por município e download do recorte |
| Gestores do SUS / analistas | Apoio à decisão | Dashboard, API e assistente de IA |
| Equipe do projeto / docente | Avaliação acadêmica | Documentação TDSP, código no GitHub |

## 6. Alinhamento entre dados, IA e engenharia de prompts e o problema de negócio

Esta seção argumenta por que cada componente é necessário para resolver o problema, e qual o seu papel em Ciência de Dados.

**Dados (matéria-prima).**
- A API de vacinação fornece o *fato* mensurável (doses por data, local, fabricante, faixa etária). Sem ela não há indicador.
- O scraping fornece o *contexto qualitativo* (campanhas, tecnologia hospitalar, notícias). Une dado estruturado e não estruturado, algo comum em projetos reais de ciência de dados.
- A etapa de preparação (remoção de colunas irrelevantes e sensíveis, imputação, padronização de textos e fabricantes) é o que torna os dados comparáveis e utilizáveis.

**Visualização e API (acesso).** Respondem à pergunta "o que aconteceu?" (análise descritiva/diagnóstica) de forma reprodutível por pessoas (Streamlit) e sistemas (FastAPI).

**IA generativa (interpretação).** O gestor nem sempre sabe que filtro ou gráfico consultar. Um LLM em linguagem natural reduz essa barreira: traduz o recorte exibido no painel em explicação e orientação, atuando como a camada "do dado ao insight". O papel em Ciência de Dados é a *comunicação de resultados* (última etapa do ciclo), e não a substituição da análise.

**Engenharia de prompts (controle).** Como o modelo é pequeno (3B) e atua em domínio sensível (saúde), o prompt é o principal mecanismo de controle:
- **papel** (`system`): especialista em saúde pública no Brasil;
- **tom e limites**: claro, acolhedor, baseado em evidências, com aviso fixo de que não substitui atendimento médico/SUS;
- **contexto** injetado: filtros ativos do painel (UF, município, período);
- **parâmetros de geração**: `temperature=0.6`, `top_p=0.9`, `max_new_tokens` ≤ 1024, timeout de 45 s.

**Por que local e open source.** Privacidade (nenhum dado sai da máquina), custo zero por token e reprodutibilidade (Apache 2.0). A comparação com o modelo descartado (27B) está no *Modeling Report*.

**Como a IA usa os dados.** Duas rotas de sumarização fecham o ciclo dados → insight: (1) notícias raspadas são resumidas em blocos (map-reduce); (2) a base filtrada vira um texto de indicadores calculados em Python, que a LLM resume. O prompt restringe o modelo aos números fornecidos. **Limite:** o modelo não lê o CSV nem verifica os números; na avaliação real, os resumos de notícias foram fiéis, mas os de dados passaram a ter números e rótulos calculados em Python (sem erro) com a LLM só interpretando, ainda com imprecisões de redação; e a latência fica entre 20 e 80 s (Evaluation Report).

## 7. Métricas de sucesso (revisadas)

Medidas sobre a base atual (`data/processed/processed_data.csv`). Detalhes no *Data Quality Report*.

| Dimensão | Meta (Q1) | Resultado | Status |
|---|---|---|---|
| Fontes integradas | ≥ 1 | 2 (API PNI + blog Medicalway) | ✅ |
| Qualidade: células não nulas | ≥ 80% | 100% após correção (95,7% antes) | ✅ |
| Cobertura temporal | ≥ 5 anos | ~5 meses (01/01–11/06/2025), irregular entre meses | ❌ |
| Cobertura regional | 100% das UFs disponíveis | 27 UFs presentes | ✅ |
| Transparência dos indicadores | 100% documentados | Dicionário de dados + este charter | ✅ |
| Dashboard funcional | Entrega | 3 páginas Streamlit | ✅ |
| API funcional | GET e POST | 2 rotas de dados + 1 rota de IA | ✅ |
| Ranking de prioridades | Top 5 | UF e vacina por volume (gráficos); ranking de "gargalos" não implementado | ⚠️ |
| IA: tempo de resposta | poucos segundos (~200 tokens) | 19–23 s (dicas), 20–27 s (resumo de dados, v4), 68–80 s (notícia) em MPS | ❌ |
| IA: qualidade das respostas | a definir | Notícias: fiéis (3/3). Dados: 0 números inventados na v2, mas com erros de associação. Dicas: erros factuais e truncamento | ⚠️ |

## 8. Riscos, premissas e limitações

| Risco / limitação | Impacto | Mitigação |
|---|---|---|
| Amostra concentrada em poucos meses (jan, fev e mai ≈ 99,9% dos registros) | Séries temporais enviesadas | Documentar; ampliar paginação/filtros de ano na coleta |
| Duplicatas (2.330 encontradas) | Contagem inflada de doses | **Corrigido**: `remove_duplicates_and_outliers` |
| Imputação (UF/município do paciente ← estabelecimento) | Viés geográfico | Declarar a regra no dicionário de dados |
| Alucinação do LLM 3B | Orientação incorreta em saúde | Prompt restritivo, aviso obrigatório, uso como apoio |
| Ausência de denominador populacional | Impossível calcular cobertura vacinal (%) | Limitar a indicadores de volume; evolução com dados do IBGE |
| Dependência de endpoint e HTML de terceiros | Quebra da coleta | Fallback para CSV local; tratar erro de rede |
| Variáveis sensíveis (raça/cor, etnia, idade) | Privacidade/LGPD | Remoção de identificadores (`codigo_paciente`, CEP etc.); uso agregado |

## 9. Papéis, cronograma e entregáveis

**Papéis:** autoria única do projeto, com acompanhamento docente (Infnet).

| Fase TDSP | Entregável | Artefato |
|---|---|---|
| Business Understanding | Charter, objetivos | este documento |
| Data Acquisition & Understanding | Coleta e perfil | `02_data_summary_report.md`, `03_data_dictionary.md` |
| Data Preparation | Base limpa | `04_data_quality_report.md` |
| Modeling | LLM e prompts | `05_modeling_report.md` |
| Evaluation | Validação | `06_evaluation_report.md` |
| Deployment / Customer Acceptance | Dashboard + API | `07_deployment_and_acceptance.md` |

## 10. Critérios de aceite

1. Dados coletados e origem documentada.
2. Base processada consistente e dicionário publicado.
3. Dashboard com filtros e indicadores funcionando.
4. Endpoints GET/POST respondendo conforme contrato.
5. Notícias coletadas e exibidas.
6. Assistente de IA respondendo via API com aviso de responsabilidade.
7. Documentação TDSP completa e coerente com o código.
