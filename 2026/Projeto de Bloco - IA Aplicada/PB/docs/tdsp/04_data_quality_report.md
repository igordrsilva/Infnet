# Data Quality Report

> Artefato TDSP · fases **Data Understanding / Data Preparation**. Base: `data/processed/processed_data.csv` (223.625 × 19 após as correções; 225.958 × 19 antes).

## 1. Resumo

| Indicador | Resultado |
|---|---|
| Células não nulas | **100%** após correção (95,7% antes) (meta Q1 ≥ 80% — atendida) |
| Linhas sem nenhum nulo | 100% após correção (31,1% antes, por `descricao_condicao_maternal`) |
| Duplicatas exatas | 0 após correção (2.330 removidas; base: 225.958 → 223.625 linhas) |
| Datas inválidas | 0% |
| Cobertura temporal | 01/01–11/06/2025; mar sem registros; abr e jun com 6 e 3 |
| Cobertura de UFs | 27 |

## 2. Problemas encontrados e tratamento

| # | Problema | Evidência | Situação | Ação recomendada |
|---|---|---|---|---|
| 1 | Cobertura temporal irregular | 99,996% dos registros em jan, fev e mai | **Aberto** | Rever paginação/filtro por data da API; documentar limitação nas análises |
| 2 | Duplicatas | 2.330 linhas idênticas | **Corrigido** | `remove_duplicates_and_outliers` no pré-processamento |
| 3 | Imputação por moda ineficaz | `fillna(lambda x: x.mode()[0])` não é suportado por pandas; havia 7,2% de nulos em tipo de estabelecimento e local de aplicação e 2,3% em fabricante | **Corrigido** | `_fill_with_mode` preenche pela moda; base final sem nulos |
| 4 | Nulos em `condicao_maternal` | 65,8% | **Corrigido** | Preenchido com "Não informado"; linhas não são mais excluídas por esta coluna |
| 5 | Fabricantes com grafias múltiplas | 3.014 valores; "Fiocruz" e "Fundacao Oswaldo Cruz", "Serum" e "Serum Institute Of India Ltd." coexistem | **Parcial** | Ampliar mapa de normalização; remover acentos |
| 6 | Outliers de idade | 2 registros > 110 anos (máx. 125) | **Corrigido** | Idades fora de 0–110 removidas (máx. atual: 108) |
| 7 | Acentuação inconsistente | `Sem Informacao`, `Espirito Santo` vs `Deltóide Direito` | **Aberto** | Padronizar (remover ou manter acentos em toda a base) |
| 8 | Redundância de arquivos | `data/processed_data.csv` idêntico a `data/processed/processed_data.csv`; `data/raw/` vazio | **Parcial** | Cópia redundante removida; `data/raw/` segue vazio (regenerar via `get_raw_data()`) |
| 9 | Fallback de notícias nunca acionado | `extract_news()` retorna `[]` em erro, e `load_news()` testa `is None` | **Corrigido** | Condição trocada para `if not news` |
| 10 | Amostra não representativa | A base é recorte da API, e não o universo do PNI | **Documentado** | Não generalizar para cobertura nacional |

## 3. Verificação das metas de qualidade do Q1

| Meta | Resultado | Observação |
|---|---|---|
| Registros válidos ≥ 80% | ✅ 100% (células e linhas) após correção | Antes: 95,7% das células e 31,1% das linhas |
| Cobertura ≥ 5 anos | ❌ ~5 meses | Limitação da coleta atual |
| 100% das UFs disponíveis | ✅ 27/27 | — |

## 4. Qualidade dos dados de notícias
- 5 notícias, 5 URLs únicas, sem título nulo; texto de ~36,8 mil a 37,2 mil caracteres cada (corpo completo).
- Risco: o seletor `a.ct-link-button` e o texto "LEIA MAIS" dependem do tema do site. Mudanças no HTML quebram a coleta; por isso o CSV serve de contingência.
- Duas das notícias têm exatamente o mesmo tamanho, o que sugere extração de modelo de página ou conteúdo repetido. Verificar se `main`/`body` está incluindo blocos fixos.

## 5. Impacto na IA
- O contexto passado ao LLM é derivado dos filtros; duplicatas e cobertura irregular afetariam qualquer agregação futura enviada ao prompt. Corrigir os itens 1–3 e 5 antes de alimentar o LLM com estatísticas.
