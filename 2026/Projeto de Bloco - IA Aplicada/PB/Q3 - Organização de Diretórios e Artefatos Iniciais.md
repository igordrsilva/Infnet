# Organização de Diretórios e Artefatos Iniciais:

1. Crie uma organização de diretórios que reflita as diferentes fases do ciclo de vida do TDSP.

PB/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── api/
│   ├── __init__.py
│   ├── model.py
│   ├── route.py
│   └── main.py
│
├── src/
│   ├── data_loader.py
│   ├── utils.py
│   ├── components/
│   │   └── news_card.py
│   │
│   ├── scraping.py
│   │
│   └── pages/
│       ├── vacinas.py
│       ├── noticias.py
│       └── dados.py
│
└── data/
    ├── raw/
    └── processed/


2. Desenvolva os artefatos iniciais do projeto, incluindo:
### Project Charter: Documento que descreve o escopo, os objetivos e os stakeholders do projeto.


**Nome do projeto:** Vacina Brasil — Análise e Monitoramento da Vacinação no Brasil

**Problema**

A disponibilidade de dados públicos sobre vacinação no Brasil não garante, por si só, que essas informações sejam facilmente exploradas e compreendidas. A necessidade de consultar diferentes fontes, analisar grandes volumes de registros e acompanhar atualizações sobre imunização dificulta a identificação de padrões e a interpretação dos dados.

Diante desse cenário, o projeto propõe desenvolver uma solução analítica para reunir, processar e disponibilizar informações sobre vacinação no Brasil, permitindo a análise de indicadores por período, estado, município e tipo de vacina, além do acompanhamento de notícias relacionadas à imunização. A iniciativa busca contribuir para a compreensão do cenário nacional de vacinação e para o acompanhamento do Objetivo de Desenvolvimento Sustentável 3 (ODS 3).

**Objetivo**

Desenvolver uma aplicação de análise e monitoramento da vacinação no Brasil, utilizando técnicas de coleta, processamento e visualização de dados. A solução deverá disponibilizar um dashboard interativo e uma API REST para consulta dos registros, permitindo explorar informações sobre vacinação por diferentes dimensões geográficas e temporais, além de acompanhar notícias relacionadas ao tema.

**Escopo**

O projeto contemplará:
* Coleta de dados públicos de vacinação por meio de fontes oficiais.
* Extração de notícias relacionadas à vacinação por web scraping.
* Utilização de automação de navegador, quando necessária, para acessar conteúdos carregados dinamicamente.
* Tratamento, limpeza e padronização dos dados coletados.
* Organização dos dados em bases brutas e processadas.
* Desenvolvimento de indicadores e análises exploratórias sobre vacinação.
* Construção de dashboard interativo com Streamlit.
* Implementação de filtros por período, estado, município e vacina.
* Disponibilização da base de dados para consulta e download.
* Desenvolvimento de API REST com FastAPI para consulta dos dados.
* Documentação das fontes, dos processos de coleta e das funcionalidades desenvolvidas.


**Stakeholders**

| Stakeholder            | Interesse                           |
| ---------------------- | ----------------------------------- |
| Ministério da Saúde    | Visão nacional dos gargalos         |
| Secretarias Estaduais  | Comparação regional                 |
| Secretarias Municipais | Identificação de prioridades locais |
| Gestores do SUS        | Apoio à decisão                     |


**Entregáveis**

* Dashboard interativo desenvolvido com Streamlit.
* API REST desenvolvida com FastAPI.
* Base de dados de vacinação tratada e organizada.
* Funcionalidade de consulta e download dos dados filtrados.
* Módulo de coleta e apresentação de notícias.
* Código-fonte e documentação técnica do projeto.

**Critérios de sucesso**

O projeto será considerado bem-sucedido caso consiga:
* Coletar dados de fontes públicas e documentar sua origem.
* Processar e disponibilizar uma base de dados consistente.
* Apresentar indicadores e visualizações relevantes sobre vacinação.
* Permitir consultas por período, estado, município e vacina.
* Disponibilizar os registros para download.
* Executar corretamente os endpoints GET e POST da API.
* Coletar e apresentar notícias relacionadas à vacinação.
* Oferecer uma aplicação funcional, organizada e de fácil utilização.


### Data Summary Report: Relacione as fontes de dados que serão utilizadas, indicando o tipo de dados e o objetivo de uso. Este será o primeiro esboço do Data Summary Report.

| Fonte                      | Tipo                               | Possíveis dados        | Objetivo                                     |
| -------------------------- | ---------------------------------- | ---------------------- | -------------------------------------------- |
| Dados Abertos Saúde Gov.br | Estruturado                        | API / requisições HTTP | Obter registros de vacinação                 |
| Dados Abertos Saúde Gov.br | Não estruturado (textual)          | Web scraping           | Coletar notícias relacionadas à vacinação    |


### Descrição das fontes
**Dados Abertos Saúde Gov.br**
Fonte principal dos dados estruturados utilizados no projeto. Fornece registros relacionados à vacinação, permitindo análises por data, localização geográfica, fabricante e tipo de dose, conforme a disponibilidade dos campos.

**Blog Medicalway**
Fonte complementar de informações textuais. A coleta é realizada por web scraping para identificar notícias e conteúdos relacionados à vacinação e à saúde.


### Variáveis a explorar

Sugiro:
* Data da vacinação.
* Unidade federativa.
* Município.
* Descrição da vacina.
* Fabricante da vacina.
* Código ou identificação da dose.