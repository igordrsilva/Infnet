## Justificativa Técnica da Escolha do Modelo de Linguagem (`Qwen/Qwen2.5-3B-Instruct`)

### 1. Seleção do Modelo e Adequação à Aplicação
Para o assistente virtual integrado ao painel de saúde pública no Brasil, foi selecionado o modelo **`Qwen/Qwen2.5-3B-Instruct`** (desenvolvido pela Alibaba Cloud e disponibilizado no Hugging Face).

Inicialmente, considerou-se o modelo `tencent/Qwen3.8-27B-DSpine-b16`, porém testes práticos no ambiente local evidenciaram limitações críticas de compatibilidade (ausência de `chat_template` configurado e falhas na tokenização de entrada) além de uma demanda computacional inviável para execução fluida em estações de trabalho locais (~54 GB de memória apenas para os pesos). A migração para o **`Qwen/Qwen2.5-3B-Instruct`** resolveu esses gargalos ao oferecer uma arquitetura consolidada, madura e amplamente suportada pela comunidade.

---

### 2. Avaliação de Arquitetura, Tarefa de Treinamento e Capacidade de Resposta
* **Arquitetura e Tipo de Tarefa:** Diferente de modelos baseados exclusivamente em *encoder* voltados para classificação ou extração (como o **BERT**) ou modelos *encoder-decoder* voltados para tradução e sumarização estruturada (como o **T5**), o `Qwen2.5-3B-Instruct` utiliza uma arquitetura **decoder-only causal** (semelhante à família GPT), otimizada especificamente para **geração autorregressiva de texto** (`AutoModelForCausalLM`).
* **Alinhamento Instrucional (*Instruct*):** Por ser uma variante *Instruct* (ajustada via *Supervised Fine-Tuning* e alinhamento de preferências humanas), o modelo compreende nativamente papéis de sistema (`system`), contexto de painel (`user`) e geração assistida (`assistant`) por meio do seu `chat_template` embutido. Isso permite controlar o tom acolhedor, informativo e responsável exigido para orientações de saúde pública.
* **Precisão e Suporte ao Português:** A família Qwen 2.5 foi treinada em um corpus multilíngue massivo (18 trilhões de tokens), apresentando alta fluência em língua portuguesa, baixa taxa de alucinação em orientações gerais e excelente capacidade de síntese quando condicionada aos filtros ativos do painel (como UF, município e período).

---

### 3. Viabilidade de Hardware e Custo Computacional Local
A escolha da versão de **3 bilhões de parâmetros (3B)** equilibra qualidade semântica e eficiência operacional no ambiente local:
* **Pegada de Memória (RAM/VRAM):** Em precisão reduzida de ponto flutuante (`float16` / `bfloat16`), o modelo ocupa aproximadamente **6 GB a 7 GB de memória**, cabendo integralmente na memória unificada de computadores modernos (como Apple Silicon via backend **MPS** ou GPUs dedicadas de entrada/intermediárias via **CUDA**), sem necessidade de *offload* lento para disco.
* **Latência de Inferência:** Enquanto modelos de 27B ou 70B parâmetros geram gargalos de minutos por requisição e *timeouts* na interface web, o porte de 3B permite respostas rápidas (na casa de poucos segundos para limites de ~200 tokens), garantindo uma experiência fluida tanto na documentação interativa do FastAPI (`/docs`) quanto no painel Streamlit.
* **Custo Zero de Infraestrutura em Nuvem:** Por rodar integralmente na máquina local sem chamadas a APIs externas (como OpenAI ou Anthropic), o projeto elimina custos recorrentes por token, evita dependência de conectividade externa em tempo de execução e preserva a privacidade dos dados consultados.

---

### 4. Acessibilidade, Licenciamento e Execução 100% Offline via Transformers
O modelo atende plenamente aos requisitos de portabilidade e integração com o ecossistema Python:
* **Licenciamento Permissivo:** Disponibilizado sob licença aberta (Apache 2.0), permite uso acadêmico, institucional e corporativo sem restrições proprietárias.
* **Integração Nativa com Hugging Face:** O modelo é baixado integralmente para o armazenamento local via `huggingface_hub` (`snapshot_download`) e carregado diretamente do disco pela biblioteca `transformers` (`AutoTokenizer` e `AutoModelForCausalLM`) com o parâmetro `local_files_only=True`.
* **Persistência em Memória:** Acoplado ao ciclo de vida (`lifespan`) do FastAPI através do gerenciador em memória (`MOTORES`), o modelo é carregado uma única vez na inicialização do servidor, mantendo a API responsiva e 100% operacional em ambiente isolado (*offline*).

---

### Síntese Comparativa da Decisão

| Critério | Modelo Descartado (`Qwen3.8-27B-DSpine-b16`) | Modelo Selecionado (`Qwen/Qwen2.5-3B-Instruct`) |
| :--- | :--- | :--- |
| **Arquitetura / Tarefa** | Causal LM (Experimental / Checkpoint específico) | Causal LM *Instruct* (Otimizado para diálogo e instruções) |
| **Consumo de Memória** | ~54 GB a 60 GB (Inviável para execução local fluida) | ~6 GB em `float16` (Compatível com MPS/GPU/RAM local) |
| **Tempo de Resposta** | Alto (Risco de *timeout* na API e no Streamlit) | Baixo (Inferência ágil para respostas objetivas) |
| **Compatibilidade Transformers** | Falhas no tokenizador e ausência de `chat_template` | Suporte nativo completo e `chat_template` validado |
| **Operação Offline** | Requer ajustes manuais de vocabulário | 100% funcional via `local_files_only=True` |