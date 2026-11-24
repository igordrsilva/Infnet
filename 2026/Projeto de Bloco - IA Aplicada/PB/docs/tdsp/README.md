# Artefatos TDSP — Vacina Brasil

Documentação do ciclo completo de ciência de dados, da obtenção dos dados à geração de insights por IA.

| Fase TDSP | Artefato |
|---|---|
| Business Understanding | [01 — Project Charter](01_project_charter.md) |
| Data Acquisition & Understanding | [02 — Data Summary Report](02_data_summary_report.md) · [03 — Dicionário de Dados](03_data_dictionary.md) |
| Data Preparation | [04 — Data Quality Report](04_data_quality_report.md) |
| Modeling | [05 — Modeling Report (LLM e prompts)](05_modeling_report.md) |
| Evaluation | [06 — Evaluation Report](06_evaluation_report.md) |
| Deployment / Customer Acceptance | [07 — Deployment e Acceptance](07_deployment_and_acceptance.md) |
| Apresentação final | [08 — Apresentação e Argumentação](08_apresentacao_e_argumentacao.md) · [deck HTML](../apresentacao/apresentacao.html) |

Histórico: `Q1`, `Q2` e `Q3` (raiz) são as versões iniciais; estes arquivos as substituem.
Documentos de apoio: `llms.md` (plano da IA) e `llm/llm.md` (justificativa do modelo).

Os números foram medidos em `data/processed/processed_data.csv` em 23/11/2026. Testes: `python -m unittest discover -s tests -t .` (31) e `python scripts/validar_llm.py` (LLM real). Visão geral e execução: [README da raiz](../../README.md).
