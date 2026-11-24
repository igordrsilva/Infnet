# Dicionário de Dados — `data/processed/processed_data.csv`

> Artefato TDSP · fase **Data Acquisition & Understanding**. 223.625 linhas × 19 colunas após as correções (225.958 antes). Os % de nulos abaixo foram medidos **antes** do preenchimento; a base atual não tem nulos (condição maternal = "Não informado").

| Coluna | Tipo | Descrição | Nulos | Tratamento / observação |
|---|---|---|---|---|
| `data_vacina` | texto (data/hora com fuso) | Data da aplicação da dose | 0% | Convertida com `pd.to_datetime` nas páginas e na API |
| `sigla_uf_estabelecimento` | texto | UF do estabelecimento de saúde | 0% | **Coluna de UF preferencial** nos filtros e na API |
| `nome_uf_estabelecimento` | texto | Nome da UF do estabelecimento | 0% | `title` |
| `nome_municipio_estabelecimento` | texto | Município do estabelecimento | 0% | **Município preferencial**; `title` |
| `descricao_tipo_estabelecimento` | texto | Tipo da unidade (ex.: Centro de Saúde/Unidade Básica) | 7,2% | Imputado pela moda (`_fill_with_mode`) |
| `sigla_uf_paciente` | texto | UF de residência do paciente | 0% | Imputada com a UF do estabelecimento quando ausente |
| `nome_uf_paciente` | texto | Nome da UF do paciente | 0% | Idem |
| `nome_municipio_paciente` | texto | Município do paciente | 0% | Imputado com o município do estabelecimento |
| `nome_pais_paciente` | texto | País do paciente | 0% | Ausente → "Brasil" |
| `descricao_nacionalidade_paciente` | texto | Nacionalidade | 0% | — |
| `nome_raca_cor_paciente` | texto | Raça/cor autodeclarada | 0% | Dado sensível; uso apenas agregado |
| `nome_etnia_indigena_paciente` | texto | Etnia indígena | 0% | Ausente → "Não Indígena" |
| `tipo_sexo_paciente` | texto | F, M ou I (indefinido) | 0% | F 123.241 · M 102.699 · I 18 |
| `numero_idade_paciente` | inteiro | Idade em anos | 0% | 0–108 após remoção de idades > 110 (2 registros removidos) |
| `descricao_condicao_maternal` | texto | Condição maternal (gestante, puérpera…) | **65,8%** | Preenchido com "Não informado" |
| `descricao_local_aplicacao` | texto | Local anatômico da aplicação | 7,2% | Ex.: Deltóide Direito |
| `codigo_vacina` | inteiro | Código do imunobiológico (77 valores) | 0% | Não há coluna com o nome da vacina na base processada; o código ainda não é usado no dashboard (oportunidade: mapear para nome do imunobiológico) |
| `codigo_dose_vacina` | inteiro | Código da dose (ex.: 1 = 1ª dose; 9 e outros códigos do PNI) | 0% | Semântica dos códigos a confirmar no dicionário oficial do PNI |
| `descricao_vacina_fabricante` | texto | Fabricante/laboratório | 2,3% | 3.014 grafias; unificação parcial por palavra-chave. **É a coluna usada como "Vacina"** nos filtros e gráficos |

## Colunas removidas no pré-processamento (33)
Códigos técnicos e de sistema (`codigo_documento`, `codigo_sistema_origem`, `codigo_via_administracao`, `codigo_origem_registro`, `codigo_troca_documento`, `status_documento`…), identificadores do estabelecimento (`codigo_cnes_estabelecimento`, `nome_razao_social_estabelecimento`, `nome_fantasia_estalecimento`…), datas de integração (`data_entrada_rnds`, `data_deletado_rnds`), e dados pessoais (`codigo_paciente`, `numero_cep_paciente`, códigos de município/país/raça/etnia do paciente). Motivos: **privacidade (LGPD)**, baixa utilidade analítica e redundância com colunas descritivas.

## Colunas usadas por cada componente
| Componente | Colunas |
|---|---|
| Filtros do dashboard | `data_vacina`, `sigla_uf_estabelecimento`, `nome_municipio_estabelecimento`, `descricao_vacina_fabricante` |
| Gráficos | `data_vacina`, UF, `descricao_vacina_fabricante` (top 15) |
| API `/vacinas` | `data_vacina`, `sigla_uf_estabelecimento`, `nome_municipio_estabelecimento` |
| Contexto da LLM | Texto dos filtros ativos (UF, município, período) |

## Dados de notícias (`data/medicalway_news.csv`)
| Coluna | Tipo | Descrição |
|---|---|---|
| `title` | texto | Título (`h1`) |
| `url` | texto | URL canônica do artigo |
| `text` | texto | Corpo extraído (`p`, `h2`, `h3`, `li`) |
