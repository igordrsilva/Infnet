# Organização do Projeto

## 1. Estruture seu projeto utilizando os métodos CRISP-DM (Cross-Industry Standard Process for Data Mining) e TDSP (Team Data Science Process).
Conforme alinhado com o professor em aula, podemos escolher entre um ou outro. Decidi utilizar o TDSP.

**Business Understanding:** 
* Definir o problema relacionado à análise e ao acompanhamento da vacinação no Brasil
* Identificar os stakeholders
* Estabelecer os objetivos e critérios de sucesso
* Delimitar o escopo da solução
* Definir as dimensões de análise: temporal, geográfica e por vacina
* Relacionar o projeto ao ODS 3 — Saúde e Bem-Estar

**Data Acquisition & Understanding:**
* Identificar e consultar fontes oficiais de dados sobre vacinação
* Consumir os dados disponibilizados pelo Dados Abertos Saúde Gov.br
* Realizar web scraping para coletar notícias relacionadas à vacinação
* Utilizar Selenium quando necessário para acessar conteúdos carregados dinamicamente
* Avaliar a estrutura, a qualidade e as limitações dos dados coletados
* Documentar a origem e o método de obtenção de cada fonte

**Data Preparation:**
* Tratamento de valores ausentes
* Tratamento de outliers
* Remoção de duplicidades
* Padronização de nomes
* Transformação de variáveis
* Criação de indicadores
* Normalização
* Conversão e padronização de datas
* Tratamento de inconsistências nos registros
* Preparação dos dados para visualização e disponibilização pela API
* Organização dos dados brutos e processados

**Modeling:**
* Análise exploratória dos dados
* Desenvolvimento de indicadores descritivos
* Agregação dos registros por período, estado, município e vacina
* Construção de métricas para apoiar a interpretação dos dados
* Desenvolvimento e organização do pipeline de processamento

**Evaluation:**
A avaliação deverá verificar se a solução atende aos objetivos definidos, considerando:
* Consistência e qualidade dos dados processados
* Funcionamento dos filtros e indicadores do dashboard
* Correção das consultas e respostas da API
* Funcionamento da coleta e apresentação das notícias
* Facilidade de navegação e compreensão das informações
* Capacidade de disponibilizar informações relevantes sobre a vacinação no Brasil

**Deployment:**
A disponibilização da solução será realizada por meio de duas aplicações independentes:
* Dashboard interativo desenvolvido com Streamlit.
* API REST desenvolvida com FastAPI, disponibilizando endpoints para consulta dos dados.

O código-fonte, a estrutura do projeto e as instruções de execução serão documentados e disponibilizados no GitHub.

## 2. Compreenda as diferentes fases do ciclo de vida do TDSP e como elas se aplicam ao seu projeto.
* Business Understanding: Compreensão do problema e definição do problema e objetivos
* Data Acquisition e Understanding: Coleta de dados e compreensão dos mesmos
* Modeling: Preparação e normalização dos dados
* Deployment: Disponibilização do dashboad
* Customer Acceptance: A solução responde/atende ao problema?