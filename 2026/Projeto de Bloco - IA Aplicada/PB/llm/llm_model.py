import os
import time
from pathlib import Path
from huggingface_hub import snapshot_download

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Garante o caminho absoluto correto independente de onde o terminal for executado
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
LOCAL_DIR = str(BASE_DIR / "models" / "Qwen2.5-3B-Instruct")


def baixar_modelo():
    print(f"Iniciando download de {MODEL_ID} para {LOCAL_DIR}...")
    os.makedirs(LOCAL_DIR, exist_ok=True)

    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=LOCAL_DIR,
        local_dir_use_symlinks=False,
        resume_download=True
    )
    print("Download concluído com sucesso! O modelo está pronto para uso offline.")


class HealthLLMService:
    def __init__(self, model_path: str = LOCAL_DIR):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None

    def is_ready(self) -> bool:
        """Verifica se o modelo e o tokenizador estão carregados na memória."""
        return self.model is not None and self.tokenizer is not None

    def load_model(self):
        """Carrega o tokenizador e o modelo na memória (MPS/GPU/CPU) a partir do disco local."""
        if self.is_ready():
            return

        if not os.path.isdir(self.model_path) or not os.listdir(self.model_path):
            raise FileNotFoundError(
                f"Diretório do modelo local não encontrado ou vazio em '{self.model_path}'. "
                "Execute 'python -m llm.llm_model' para baixar os arquivos."
            )

        print(f"Carregando modelo local de: {self.model_path}...")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True
            )

            if torch.backends.mps.is_available():
                device = "mps"
                dtype = torch.float16
            elif torch.cuda.is_available():
                device = "cuda"
                dtype = torch.bfloat16
            else:
                device = "cpu"
                dtype = torch.float32

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                dtype=dtype,
                local_files_only=True
            ).to(device)

            self.model.eval()
            print(f"Modelo carregado com sucesso em '{device}' ({dtype}) e pronto para inferência.")
        except Exception as e:
            self.tokenizer = None
            self.model = None
            raise RuntimeError(f"Falha crítica ao carregar os pesos da LLM na memória: {str(e)}") from e

    def generate_health_tip(
        self,
        user_input: str,
        context: str = "",
        max_new_tokens: int = 200,
        timeout_segundos: float = 45.0
    ) -> tuple[str, float]:
        """Gera dicas de saúde e retorna (texto_gerado, tempo_em_segundos)."""
        if not self.is_ready():
            raise RuntimeError("O modelo LLM não está carregado na memória.")

        inicio = time.perf_counter()

        system_prompt = (
            "Você é um assistente virtual especialista em saúde pública e bem-estar no Brasil. "
            "Forneça dicas de saúde claras, acolhedoras, objetivas e baseadas em evidências para os visitantes "
            "de um painel de indicadores de saúde. Sempre lembre o usuário de que suas dicas são "
            "informativas e não substituem uma consulta médica ou atendimento no SUS."
        )

        user_content = user_input.strip()
        if context and context.strip():
            user_content = f"Contexto do painel de saúde: {context.strip()}\nPergunta do visitante: {user_content}"

        if getattr(self.tokenizer, "chat_template", None):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            text = (
                f"Instruções: {system_prompt}\n\n"
                f"{user_content}\n\n"
                f"Resposta:"
            )

        model_inputs = self.tokenizer(
            text,
            return_tensors="pt",
            add_special_tokens=True
        )

        if model_inputs["input_ids"].shape[1] == 0:
            raise ValueError("O tokenizador gerou uma sequência vazia (0 tokens) para o prompt informado.")

        model_inputs = {k: v.to(self.model.device) for k, v in model_inputs.items()}
        pad_id = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id

        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids=model_inputs["input_ids"],
                attention_mask=model_inputs["attention_mask"],
                max_new_tokens=max_new_tokens,
                max_time=timeout_segundos,
                temperature=0.6,
                top_p=0.9,
                do_sample=True,
                pad_token_id=pad_id,
                eos_token_id=self.tokenizer.eos_token_id,
                use_cache=True
            )

        tempo_decorrido = round(time.perf_counter() - inicio, 2)

        input_length = model_inputs["input_ids"].shape[1]
        new_tokens = generated_ids[0][input_length:]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        if not response:
            raise RuntimeError("O modelo concluiu a execução, mas não retornou texto válido.")

        return response, tempo_decorrido


# Dicionário compartilhado entre api/main.py e api/route.py
MOTORES: dict[str, HealthLLMService] = {}


def carregar_llm() -> HealthLLMService:
    """Instancia e carrega o modelo na memória (chamado pelo lifespan da API)."""
    servico = HealthLLMService()
    servico.load_model()
    return servico


if __name__ == "__main__":
    baixar_modelo()