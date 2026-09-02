# Organização de Diretórios e Artefatos Iniciais:

1. Crie uma organização de diretórios que reflita as diferentes fases do ciclo de vida do TDSP.

TP1/
│
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── ibge.csv
│   │   └── outras_fontes.csv
│   │
│   └── processed.csv
│
├── src/
│   ├── ingestion.py
│   ├── preprocessing.py
│   ├── modeling.py
│
└── app.py


2. Desenvolva os artefatos iniciais do projeto, incluindo:
### Project Charter: Documento que descreve o escopo, os objetivos e os stakeholders do projeto.


**Nome do projeto:** HealthGap Brasil — Identificação dos principais gargalos da saúde pública brasileira

**Problema**

A grande quantidade e dispersão de dados públicos de saúde dificultam a identificação objetiva das áreas que apresentam os maiores problemas no atendimento e no bem-estar da população brasileira.

**Objetivo**

Desenvolver uma solução analítica capaz de integrar indicadores públicos de saúde e identificar as cinco áreas que apresentam os maiores gargalos no setor público brasileiro.

**Escopo**

O projeto contemplará:

* coleta de dados públicos;
* integração das fontes;
* tratamento e padronização;
* criação de indicadores;
* construção de índice de gargalo;
* ranking das áreas;
* análise regional;
* visualização dos resultados.


**Stakeholders**

| Stakeholder            | Interesse                           |
| ---------------------- | ----------------------------------- |
| Ministério da Saúde    | Visão nacional dos gargalos         |
| Secretarias Estaduais  | Comparação regional                 |
| Secretarias Municipais | Identificação de prioridades locais |
| Gestores do SUS        | Apoio à decisão                     |


**Entregáveis**

* Índice de Gargalo.
* Ranking das cinco áreas.
* Dashboard.

**Critérios de sucesso**

O projeto será considerado bem-sucedido caso consiga:

* integrar fontes confiáveis;
* produzir indicadores reproduzíveis;
* identificar cinco áreas prioritárias;
* permitir análise regional;
* disponibilizar os resultados de maneira compreensível.

### Data Summary Report: Relacione as fontes de dados que serão utilizadas, indicando o tipo de dados e o objetivo de uso. Este será o primeiro esboço do Data Summary Report.

| Fonte               | Tipo           | Possíveis dados                                | Objetivo                         |
| ------------------- | -------------- | ---------------------------------------------- | -------------------------------- |
| DATASUS             | Dados de saúde | Indicadores, atendimentos, internações         | Base principal                   |
| CNES                | Estruturado    | Hospitais, profissionais, leitos, equipamentos | Medir capacidade da rede         |
| SIH/SUS             | Estruturado    | Internações hospitalares                       | Avaliar demanda e atendimento    |
| SIM                 | Estruturado    | Mortalidade                                    | Avaliar resultados de saúde      |
| SINASC              | Estruturado    | Nascimentos e informações materno-infantis     | Avaliar saúde materna e infantil |
| OpenDataSUS         | Estruturado    | Diversos conjuntos de saúde                    | Complementar indicadores         |
| IBGE                | Estruturado    | População, renda, território, demografia       | Criar taxas e contextualização   |
| IPEA                | Estruturado    | Indicadores socioeconômicos                    | Analisar desigualdades           |
| Ministério da Saúde | Estruturado    | Indicadores e políticas públicas               | Complementar dados oficiais      |


**Variáveis a explorar**

* número de médicos;
* enfermeiros;
* leitos;
* hospitais;
* unidades de saúde;
* mortalidade;
* população;
* orçamento.