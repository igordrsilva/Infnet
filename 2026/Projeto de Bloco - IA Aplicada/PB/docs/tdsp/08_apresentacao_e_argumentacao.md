# Apresentação e Argumentação da Solução Final

> Artefato TDSP · fase **Customer Acceptance / Apresentação final**. Resume, para a banca, como o projeto resolve o problema de negócio, qual o papel de cada etapa do ciclo de ciência de dados, o que foi validado com dados reais e com a LLM real, e o que ainda é limitação. Deck: [`docs/apresentacao/apresentacao.html`](../apresentacao/apresentacao.html).

## 1. Problema de negócio, em uma frase

**Gestores e analistas do SUS precisam enxergar rapidamente onde, quando e com quais vacinas as doses estão sendo registradas e onde há lacunas, mas os dados públicos são volumosos, sujos e separados das notícias do setor.**

Sem apoio, responder "onde estão concentradas as doses e o que falta nos dados?" exige baixar centenas de milhares de linhas, limpar, agregar e ainda interpretar. A solução reduz isso a **2 seleções e 1 clique** (UF e mês → interpretação ou pergunta à IA).

- **Público:** gestores e analistas de planejamento em saúde (estaduais, municipais e do SUS).
- **Decisão apoiada:** priorizar atenção a regiões, períodos e faixas etárias com baixa ou irregular cobertura de **registros**, e identificar falhas na própria base.
- **ODS:** ODS 3 — Saúde e Bem-Estar (§5).

## 2. A solução em uma imagem

```
API Gov.br (PNI) ──┐                                         ┌─► Gráficos e indicadores (Python)
                   ├─► Preparação ─► Base processada ─► Análise ─┤
Blog (scraping) ───┘   (limpeza)      223.625 linhas            └─► LLM local (Qwen2.5-3B)
                                                                      ├─ interpreta o recorte (sem números)
                                                                      ├─ responde perguntas (números verificados)
                                                                      └─ resume notícias (map-reduce)
                                                  Dashboard Streamlit ◄───┘  ·  API FastAPI
```

**Decisão de arquitetura central:** *os números vêm do Python e a IA só interpreta.* Isso nasceu de um problema medido (§4.4): quando a LLM calculava ou citava números livremente, ela inventou percentuais e trocou rótulos.

## 3. Por que cada etapa do ciclo de ciência de dados importa

| Etapa (TDSP) | O que foi feito | Por que importa para o problema | Evidência real |
|---|---|---|---|
| **1. Entendimento do negócio** | Charter, stakeholders, métricas de sucesso, riscos | Evita construir um painel sem decisão associada; define o que é sucesso (e o que **não** dá para afirmar) | Reconciliação do Q1 (gargalos) com o escopo real (vacinação); limitação declarada: sem população-alvo, **não há cobertura vacinal** |
| **2. Coleta** | API paginada (1.000 por página) e scraping com `requests` + `BeautifulSoup`; fallback para CSV | Dado oficial e atual é a base de toda confiança; texto não estruturado traz contexto | 223.625 registros, 27 UFs, 5.224 municípios, 5 notícias; fallback de notícias funcionou quando o blog devolveu HTTP 406 |
| **3. Limpeza e preparação** | Remoção de 33 colunas (dados pessoais/técnicos), imputação, duplicatas, idades fora de 0–110, padronização | Dado sujo gera indicador errado e IA errada; remover dados pessoais atende LGPD | 2.330 duplicatas removidas; 95,7% → 100% das células preenchidas; idade máxima 125 → 108 |
| **4. Exploração e indicadores** | Doses por mês/UF/fabricante/faixa etária; qualidade ao vivo | Mostra padrões **e problemas dos dados** | Março sem registros; maio concentra 51,4% das doses; SP 20,9%; 47,9% dos registros são de menores de 12 anos e 14,6% de 60+ |
| **5. Modelagem (IA)** | Escolha do modelo, engenharia de prompts, abordagem híbrida, verificação automática | Transforma números em linguagem que o gestor usa, **sem** perder a exatidão | 4 iterações de prompt medidas (§4.4); 0 números não verificados nas perguntas finais |
| **6. Avaliação** | 31 testes automatizados + validação com LLM real + protocolo com notas | Mostra o que funciona e o que não funciona, com números | §4 |
| **7. Implantação e apresentação** | Dashboard (4 abas) e API (documentação em `/docs`), status da IA, degradação elegante | O insight só vale se for usável por quem decide | Teste real no navegador; barra lateral indica IA online/offline |

## 4. Uso de dados reais e de IA: o que foi validado

### 4.1 Dados reais
Todos os números do dashboard vêm da base real coletada da API do Ministério da Saúde (doses aplicadas PNI, 2025) e de notícias reais do blog Medicalway. **Nenhum dado foi simulado.** Ressalva: é um recorte da API (jan–jun/2025, irregular), não o universo do PNI.

### 4.2 Testes automatizados (31, todos passando)
`python -m unittest discover -s tests -t .` (LLM simulada, base real):

| Suíte | Testes | O que cobre |
|---|---|---|
| `test_preprocessing` | 4 | imputação, duplicatas/outliers, normalização de fabricantes |
| `test_summarizer` | 5 | divisão de texto, filtro "sem números", verificação de números, aviso das dicas |
| `test_insights` | 5 | destaques com números exatos, meses sem registro, séries dos gráficos |
| `test_api` | 12 | rotas de dados e de IA, erros 400/422/503, map-reduce, descarte de interpretação com números, histórico |
| `test_dashboard` | 5 | página do ciclo (4 abas), filtro por UF, interpretação, chat com aviso, API offline |

### 4.3 Validação ponta a ponta com a LLM real (`scripts/validar_llm.py`, 23/11/2026)
Qwen2.5-3B-Instruct, float16, backend MPS, 16 chamadas reais (`llm/output/validacao_final.json`):

| Função | Casos | Resultado | Tempo médio |
|---|---|---|---|
| Resumo de notícia | 5 | 5/5 no formato esperado (Tema · Pontos principais · Relevância); fatos conferidos no texto original (ex.: BeneVision, N15/N17, RDC-07) | 72,9 s |
| Interpretação do recorte | 3 | 3/3 sem algarismos (garantido por código); números dos destaques 100% exatos | 22,0 s |
| Perguntas sobre os dados | 5 | 3 respostas numéricas corretas e 2 recusas corretas (cobertura vacinal e detalhe por município não existem no resumo); **0 números não verificados** | 6,4 s |
| Dicas de saúde | 3 | 3/3 com o aviso de responsabilidade (anexado por código); pedido de diagnóstico foi recusado com orientação a procurar atendimento | 21,3 s |

### 4.4 O que a validação revelou (e como o projeto reagiu)

| Iteração | Problema medido | Reação |
|---|---|---|
| v1 (resumo livre) | Inventou "62,3% de menores de 12" (real: 47,9%); "distribuição uniforme" falso | Regras no prompt |
| v2 (regras de prompt) | 0 números inventados, mas **rótulo trocado** (RJ com o valor do PR) | Abandonar números gerados pela LLM |
| v4 (híbrido) | Números e rótulos exatos por construção; LLM só interpreta | Filtro por código descarta frases com dígitos; 2ª tentativa; se nada sobrar, só o template |
| Perguntas | Risco de invenção em respostas numéricas | Verificação automática dos números e aviso na tela |
| Dicas | Respostas cortadas, sem o aviso | Corte da frase incompleta e aviso anexado por código |

### 4.5 Limitações que continuam (honestidade)
- **Redação do modelo de 3B ainda tem erros.** Na validação final, as interpretações trouxeram "série temporária" (em vez de "temporal"), "três estados brasileiras" e, no recorte nacional, "distribuição regional equilibrada" (os números não sustentam isso: SP tem 20,9%). No recorte de SP, a frase "falhas na logística de vacinação" é uma causa que os dados não comprovam. **Por isso os números ficam sempre ao lado do texto e a tela rotula o parágrafo como "Interpretação (IA)".**
- **Sem cobertura vacinal:** a base não tem população-alvo. O sistema diz isso, e o chat se recusa a afirmar cobertura.
- **Cobertura temporal:** ~5 meses, irregulares (março sem registro). Meta original de 5 anos não foi atendida.
- **Latência:** 6 a 100 s, bem acima de "tempo real". Notícias (3 chamadas com ~1,5 mil tokens) são o ponto mais lento.
- **Fabricantes** ainda aparecem com grafias duplicadas nos gráficos ("Fiocruz", "Fio Cruz", "Fundacao Oswaldo Cruz").
- **Dicas de saúde** usam conhecimento geral do modelo, não os dados; já tiveram erros factuais na avaliação anterior (ex.: citar varíola como vacina da caderneta). O aviso é obrigatório, mas o conteúdo exige revisão.
- **Sem memória conversacional:** cada pergunta é independente.

## 5. Alinhamento aos ODS e às práticas de ESG

O enunciado cita sustentabilidade e governança; este projeto é de **saúde pública**, então o alinhamento é feito às dimensões de ESG que de fato se aplicam, sem forçar o que não se mede.

| Dimensão | Como o projeto se alinha | Evidência no projeto | Limite / não medido |
|---|---|---|---|
| **ODS 3 — Saúde e Bem-Estar** (metas 3.8 e 3.b) | Apoia o acompanhamento do acesso a vacinas por UF, mês e faixa etária | Dashboard com recorte por UF e mês; perfil etário (14,6% de 60+) | Não calcula cobertura; mede doses registradas |
| **ODS 16 — Instituições eficazes e transparentes** (16.6 e 16.10) | Usa dados abertos oficiais e torna a análise **auditável** | Contexto enviado à IA visível; números verificados; histórico de toda interação em `llm/output/historico.jsonl`; qualidade da base exibida ao vivo | O histórico é local, sem trilha de acesso por usuário |
| **ODS 10 — Redução das desigualdades** (apoio) | Comparação regional e etária pode expor desigualdades de registro | Doses por UF e faixa etária | Não há análise de equidade (sem população) |
| **ESG · Social (S)** | Saúde da população; atenção a grupos (crianças, idosos) | Indicadores por faixa etária | Dados de raça/cor e etnia não são usados nas análises |
| **ESG · Governança (G)** | Governança de **dados** e de **IA** | LGPD: 33 colunas pessoais/técnicas removidas; IA com guardrails (papel, fonte restrita, verificação, aviso); humano decide; transparência dos limites (qualidade, cobertura, o que a IA não sabe) | Não há DPO, política formal nem avaliação de viés |
| **ESG · Ambiental (E)** | LLM pequena **local** evita chamadas a serviços em nuvem e mantém os dados na máquina | Modelo 3B (~6 GB), sem API externa | **Consumo de energia não foi medido**; não há alegação de ganho ambiental |

## 6. Simplicidade de uso × profundidade dos insights

**Simplicidade (para o gestor):**
- Página inicial única, com fluxograma das 5 etapas e **4 abas em ordem lógica** (Coleta → Preparação → IA aplicada → Pergunte à IA).
- **2 seleções** (UF e mês) controlam todos os gráficos, o resumo e o chat.
- **1 clique** gera a interpretação; perguntas sugeridas evitam a "página em branco".
- Estado da IA sempre visível; se a API estiver fora, o dashboard avisa e continua útil.

**Profundidade (por baixo):**
- Qualidade medida ao vivo, antes e depois da limpeza.
- Destaques com **alertas de lacuna** (meses com < 1% dos registros) calculados por código.
- IA com 4 técnicas combinadas: papel, *grounding*, formato estruturado, map-reduce; mais **verificação automática** e **descarte por código** do que viola a regra.
- Cada resposta mostra o contexto usado, o modelo e o tempo.

## 7. Roteiro de demonstração (≈ 6 minutos)

| Min | Aba / ação | Fala-chave |
|---|---|---|
| 0:00 | Slide do problema | "Dados abertos existem; interpretá-los é o gargalo do gestor." |
| 1:00 | Fluxograma do dashboard | "Cinco etapas; vou mostrar cada uma." |
| 1:30 | **1 · Coleta** | "Duas fontes reais: API do Ministério e blog; 223.625 registros, 27 UFs." |
| 2:15 | **2 · Preparação** | "Removemos 2.330 duplicatas e dados pessoais; 100% preenchida. Note que **março está vazio**: a limpeza revela o problema, não o esconde." |
| 3:00 | **3 · IA aplicada**: escolher **SP** | "Os números são do Python. Clique em *Gerar interpretação*: a IA só escreve o parágrafo, sem números." |
| 4:00 | Mostrar uma imprecisão da IA | "Por isso o texto é rotulado e os números ficam ao lado." |
| 4:30 | **4 · Pergunte à IA**: "Qual o mês com mais doses?" e depois "Qual a cobertura vacinal em MG?" | "Responde com números verificados e **recusa** o que os dados não permitem." |
| 5:30 | Slide ODS/ESG e limitações | "ODS 3 e 16; governança de dados e de IA; o que ainda não fazemos." |

## 8. Próximos passos
1. Ampliar a coleta temporal e incluir **população-alvo (IBGE)** para calcular cobertura vacinal real.
2. Normalizar fabricantes e acentuação.
3. Reduzir a latência (menos blocos por notícia, quantização ou modelo/API maior) e testar um modelo maior para a redação.
4. Memória conversacional (Opção 1) sobre o chat.
5. Medir consumo de energia da inferência para sustentar qualquer alegação ambiental.
6. Trilha de auditoria por usuário e avaliação de viés, se houver uso institucional.

## 9. Mapa dos artefatos

| Pergunta da banca | Onde está |
|---|---|
| Qual é o problema e o escopo? | [01 — Project Charter](01_project_charter.md) |
| De onde vêm os dados e como foram integrados? | [02 — Data Summary Report](02_data_summary_report.md), [03 — Dicionário](03_data_dictionary.md) |
| Qual a qualidade dos dados? | [04 — Data Quality Report](04_data_quality_report.md) |
| Como a IA foi escolhida e instruída? | [05 — Modeling Report](05_modeling_report.md) |
| Como foi validada? | [06 — Evaluation Report](06_evaluation_report.md), `tests/`, `scripts/validar_llm.py` |
| Como executar e usar? | [07 — Deployment](07_deployment_and_acceptance.md), [README](../../README.md) |
