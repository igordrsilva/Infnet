# Modeling Report — IA generativa e engenharia de prompts

> Artefato TDSP · fase **Modeling**. Neste projeto, a "modelagem" é a camada de **IA generativa** (LLM) e o desenho dos prompts, além dos indicadores descritivos. Não há modelo preditivo treinado.

## 1. Papel da modelagem no problema de negócio
O gestor precisa **interpretar** o recorte exibido (UF, município, período). O LLM converte esse contexto em linguagem natural, completando o ciclo: coleta → preparação → indicadores → **interpretação por IA**.

## 2. Indicadores descritivos (modelagem analítica)
Total de doses, UFs, municípios e vacinas distintas; série temporal diária; doses por UF; doses por vacina/fabricante (top 15). São agregações do `groupby` sobre a base filtrada (`src/pages/vacinas.py`).

## 3. Seleção do modelo de linguagem

| Critério | `tencent/Qwen3.8-27B-DSpine-b16` (descartado) | `Qwen/Qwen2.5-3B-Instruct` (escolhido) |
|---|---|---|
| Arquitetura | Causal LM (checkpoint específico) | Causal LM *Instruct* (decoder-only) |
| Memória | ~54–60 GB | ~6–7 GB em float16 |
| Compatibilidade | Sem `chat_template`; falhas de tokenização | Suporte nativo e `chat_template` |
| Latência | Alta, com risco de timeout | Segundos para ~200 tokens |
| Operação | Ajustes manuais | 100% offline (`local_files_only=True`) |

Por que decoder-only *Instruct* e não BERT/T5: a tarefa é **geração de texto condicionada a instruções e contexto**. BERT (encoder) é voltado à classificação/extração, e T5 (encoder-decoder) à tradução/sumarização estruturada. Justificativa completa em `llm/llm.md`.

Outros motivos: licença Apache 2.0, bom português, custo zero por token, privacidade (sem chamadas a APIs externas) e carregamento único no `lifespan` do FastAPI (`MOTORES`).

Seleção de dispositivo: MPS (Apple Silicon, float16) → CUDA (bfloat16) → CPU (float32).

## 4. Engenharia de prompts (implementada em `llm/llm_model.py`)

| Elemento | Implementação | Objetivo |
|---|---|---|
| Papel | `system`: "assistente virtual especialista em saúde pública e bem-estar no Brasil" | Ancorar domínio e idioma |
| Tom | claras, acolhedoras, objetivas, baseadas em evidências | Adequação ao público gestor/visitante |
| Salvaguarda | Sempre lembrar que as dicas são informativas e não substituem consulta médica/SUS | Mitigar risco em saúde |
| Contexto | `"Contexto do painel de saúde: {contexto}\nPergunta do visitante: {pergunta}"` | Condicionar a resposta aos filtros do painel |
| Template | `tokenizer.apply_chat_template` (`system` + `user`); *fallback* textual se não houver template | Compatibilidade entre modelos |
| Amostragem | `temperature=0.6`, `top_p=0.9`, `do_sample=True` | Equilíbrio entre fluidez e consistência |
| Limites | `max_new_tokens` 50–1024 (padrão 200), `max_time=45 s` | Controlar latência e custo |
| Validação de entrada | Pydantic: `query` 3–1000 caracteres; `contexto_painel` ≤ 1500 | Robustez e segurança |

## 4.1 Caminho escolhido: Sumarização de textos e dados (Opção 2) — implementada

Escolhida por ser a mais simples sobre o que já existia (notícias raspadas + LLM local + API). Código: `llm/summarizer.py`, `llm/llm_model.py` (`summarize_news`, `summarize_data`), `src/insights.py`, rotas em `api/route.py`, botões em `src/pages/`.

| Aspecto | Notícias (`POST /llm/resumo`) | Dados (`POST /llm/resumo-dados`) |
|---|---|---|
| Entrada | Título + texto da notícia raspada | Recorte filtrado (a API calcula, ou o dashboard envia `destaques` e `indicadores` prontos) |
| Pré-processamento | Texto truncado em 12.000 caracteres e dividido em blocos de ~6.000 | `build_highlights` (template Python: panorama, mês de pico, top UFs ou municípios, top fabricantes, faixa etária, meses com < 1% dos registros) e `build_data_context` (indicadores detalhados) |
| Estratégia | **Map-reduce**: resumo de cada bloco (≤150 tokens) → resumo executivo final | **Abordagem híbrida**: números e rótulos por template em Python (sem IA); a LLM escreve só um parágrafo de interpretação **sem algarismos** |
| Prompt de sistema | Analista de comunicação em saúde; usar APENAS o texto; não inventar | Analista de saúde pública; interpretar o resumo numérico sem usar algarismos (usar "mais da metade" etc.), sem inventar causas, sem criticar o recorte |
| Formato de saída | **Tema** · **Pontos principais** (3) · **Relevância para a gestão** | **Panorama** · **Destaques** · **Pontos de atenção** (template) + **Interpretação (IA)** (1 parágrafo) |
| Temperatura | 0,2 (fidelidade) | 0,2 |
| Registro | `llm/output/historico.jsonl` (tipo, entrada, saída, tempo, modelo) | idem |

Técnicas de engenharia de prompts aplicadas: papel (*role prompting*), restrição de fonte (*grounding* — “use apenas o texto/números abaixo”), formato de saída estruturado, decomposição em etapas (map-reduce), temperatura baixa e transparência (a interface mostra os indicadores enviados à IA).

Fluxo: dado coletado (scraping/API) → transformação (`preprocessing`, `insights`) → prompt → LLM local → resumo exibido no Streamlit e registrado em `llm/output`.

## 4.2 Perguntas e respostas sobre os dados (dashboard final)

Rota `POST /llm/pergunta-dados` (`answer_question`). Fluxo: o dashboard monta o resumo numérico do recorte (UF e mês) por template → envia com a pergunta → a LLM responde → a API verifica se todo número da resposta aparece no contexto (`numeros_nao_verificados`) e a interface exibe um aviso se houver algum.

| Elemento | Escolha |
|---|---|
| Prompt de sistema | Analista do SUS; responder SOMENTE com o resumo; copiar números exatamente; se faltar informação, dizer que o recorte não permite responder e sugerir ajustar o recorte; não afirmar cobertura vacinal, causas ou recomendações clínicas; até 4 frases |
| Temperatura | 0,1 (respostas factuais) |
| Contexto | `build_highlights` do recorte (≈ 1 mil caracteres) |
| Verificação | Comparação dos números da resposta com o contexto e com a pergunta (por dígitos) |
| Registro | `llm/output/historico.jsonl` (tipo `pergunta_dados`) |

Sem memória conversacional: cada pergunta é independente (o histórico do chat é só visual). Evolução natural: Opção 1 (memória) sobre este chat.

## 5. Limitações conhecidas
1. A rota `/llm/dica-saude` continua recebendo só texto de contexto; **as rotas de resumo** (§4.1) é que trabalham sobre notícias e indicadores da base. A LLM não consulta a base diretamente: recebe agregados calculados em Python, e não verifica os números.
2. O Streamlit chama a API por HTTP (`API_LLM_URL`, padrão `http://localhost:8000`); a API precisa estar rodando e com o modelo baixado.
3. Resumos de notícias cobrem só os primeiros 12.000 caracteres (limite de latência).
4. Modelo 3B: risco de alucinação, com mitigação apenas por prompt.
5. Resposta cortada em `max_new_tokens` pode terminar no meio da frase.
6. `max_time` interrompe a geração e retorna texto parcial; o `TimeoutError` tratado na rota não é lançado pelo modelo.

## 6. Evolução proposta
1. ~~Prompt com agregações~~, ~~prompt "analista"~~, ~~logging~~ e ~~integração à UI~~ — implementados em §4.1.
2. **Memória conversacional (Opção 1):** reaproveitar o resumo como contexto inicial de um chat.
3. **RAG simples:** cruzar notícias e indicadores no mesmo prompt.
4. **Verificação automática:** conferir se os números do resumo existem nos indicadores enviados.

## 7. Experimentos de prompt (a registrar)
Cada variação deve ser anotada na tabela abaixo, com as mesmas perguntas do *Evaluation Report*.

| Versão | Mudança | Resultado | Decisão |
|---|---|---|---|
| v1 | Prompt de dicas (gerais + contexto textual) | Dicas truncadas, com 2 erros factuais em 3 perguntas gerais; ignorou o contexto em 1 | Mantido; ajustar `max_tokens` e aviso |
| v2a | Resumo de dados com agregações (sem regras anti-invenção) | 1 número inventado em 3 recortes (62,3%) | Substituído |
| v2b | v2a + 4 regras (citar só números literais; não criticar o recorte; fabricantes ≠ produtores; sem afirmações causais) | 0 números inventados; ainda há erros de associação (RJ ↔ 13.805) e crítica ao recorte; +25–35% de latência | Substituído pela v4 |
| v4 | **Híbrido (adotado)**: destaques por template + LLM só para interpretação sem números; saída filtrada por código (descarta frases com dígitos ou cortadas; 2ª tentativa; se nada restar, só o template) | Números e rótulos 100% corretos por construção; 3/3 interpretações sem algarismos; 20–27 s; ainda há imprecisões qualitativas (ver Evaluation Report §3.2) | **Adotado** |
| v3 | Resumo de notícias em map-reduce (`resumo`) | 3/3 fiéis ao texto (números e normas conferidos); 68–80 s | **Adotado** |

**Aprendizado:** o modelo de 3B segue bem formato e papel, e é fiel em resumo de texto corrido. Falha em ligar rótulos a números de uma lista e ignora parte das regras negativas. Para dados, o caminho adotado (v4) é calcular os destaques em Python e usar a LLM só para a interpretação. Isso eliminou os erros de associação número–rótulo por construção; sobram imprecisões qualitativas na redação.
