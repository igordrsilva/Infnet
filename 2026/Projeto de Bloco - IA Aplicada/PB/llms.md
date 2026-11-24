#  Preparação para Uso de Inteligência Artificial com LLMs
## Objetivo
Aqui vamos ter como objetivo implementar LLMs para auxiliar na análise dos dados. Servirá como um sistema de perguntas e respostas.

## Fonte de dados consultada
Disponibilizaremos à LLM a base de dados já processada. À partir dela, a IA poderá responder as perguntas feitas à ela.

## Output
Teremos uma sub-pasta no projeto chamada `/llm`, onde desenvolveremos as integrações e chaves de acesso da LLM utilizada. Além disso, dentro da mesma, teremos uma pasta chamada `/llm/output` onde ficarão centralizadas as perguntas e respostas da IA. Dessa forma, facilitará a consulta das respostas e o histórico das perguntas.

## Atualização — caminho implementado: sumarização (Opção 2)
- **Notícias:** `POST /llm/resumo` resume o texto raspado em blocos (map-reduce).
- **Dados:** `POST /llm/resumo-dados` monta os destaques numéricos por template (`build_highlights` em `src/insights.py`, sem IA) e usa a LLM apenas para um parágrafo de interpretação sem algarismos, filtrado por código. A LLM não lê o CSV.
- **Output:** `llm/output/historico.jsonl` guarda tipo, entrada, saída, tempo e modelo de cada interação.
- **Perguntas:** `POST /llm/pergunta-dados` responde sobre o recorte (UF/mês) usando só o resumo numérico, e sinaliza números que não estejam no contexto.
- **Dashboard:** a página "Ciclo de Dados e IA" reúne coleta, preparação, gráficos, interpretação por IA e chat.
- **Interface:** botões "Resumir com IA" (Notícias) e "Gerar resumo dos dados filtrados" (Vacinas), que chamam a API.
