import os
import tempfile
import unittest
from datetime import date

from fastapi.testclient import TestClient

from llm import summarizer
from llm.llm_model import MOTORES, HealthLLMService

ARQ = "data/processed/processed_data.csv"


class FakeLLM(HealthLLMService):
    """LLM simulada: devolve respostas programadas sem carregar o modelo."""

    def __init__(self):
        super().__init__()
        self.saidas = []
        self.chamadas = []

    def is_ready(self):
        return True

    def _chat(self, system_prompt, user_content, max_new_tokens, temperature, timeout_segundos):
        self.chamadas.append((system_prompt, user_content, temperature))
        return self.saidas.pop(0)


@unittest.skipUnless(os.path.exists(ARQ), "base processada ausente")
class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api.main import app

        tmp = tempfile.mkdtemp()
        cls._orig = (summarizer.OUTPUT_DIR, summarizer.HISTORICO_PATH)
        summarizer.OUTPUT_DIR = type(cls._orig[0])(tmp)
        summarizer.HISTORICO_PATH = summarizer.OUTPUT_DIR / "h.jsonl"
        cls.client = TestClient(app)  # sem `with`: o lifespan (modelo real) não roda

    @classmethod
    def tearDownClass(cls):
        summarizer.OUTPUT_DIR, summarizer.HISTORICO_PATH = cls._orig

    def setUp(self):
        MOTORES.clear()
        self.llm = FakeLLM()
        MOTORES["llm_saude"] = self.llm

    def tearDown(self):
        MOTORES.clear()

    # --- dados ---
    def test_get_vacinas_filtra_por_uf_e_limite(self):
        r = self.client.get("/vacinas", params={"uf": "SP", "limite": 5})
        self.assertEqual(r.status_code, 200)
        j = r.json()
        self.assertEqual(j["total_registros"], 5)
        self.assertTrue(all(d["sigla_uf_estabelecimento"] == "SP" for d in j["dados"]))

    def test_post_consulta_por_periodo(self):
        r = self.client.post("/vacinas/consulta", json={"data_inicio": "2025-02-01", "data_fim": "2025-02-28", "limite": 20})
        self.assertEqual(r.status_code, 200)
        for d in r.json()["dados"]:
            self.assertTrue(d["data_vacina"].startswith("2025-02"))

    def test_erros_padronizados(self):
        r = self.client.get("/vacinas", params={"data_inicio": "2025-05-01", "data_fim": "2025-01-01"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["status"], "erro")
        self.assertEqual(self.client.get("/vacinas", params={"uf": "SAO"}).status_code, 422)

    # --- IA ---
    def test_status(self):
        self.assertTrue(self.client.get("/llm/status").json()["pronto"])
        MOTORES.clear()
        self.assertFalse(self.client.get("/llm/status").json()["pronto"])

    def test_sem_llm_retorna_503(self):
        MOTORES.clear()
        for rota, corpo in [
            ("/llm/resumo", {"texto": "x" * 60}),
            ("/llm/resumo-dados", {}),
            ("/llm/pergunta-dados", {"pergunta": "Qual UF lidera?"}),
            ("/llm/dica-saude", {"query": "vacinas para idosos"}),
        ]:
            self.assertEqual(self.client.post(rota, json=corpo).status_code, 503, rota)

    def test_resumo_noticia_map_reduce(self):
        self.llm.saidas = ["parcial 1", "parcial 2", "RESUMO FINAL"]
        texto = ("Vacinação é importante. " * 300 + "\n") * 6
        j = self.client.post("/llm/resumo", json={"titulo": "T", "texto": texto}).json()
        self.assertEqual(j["blocos_processados"], 2)
        self.assertEqual(j["resumo"], "RESUMO FINAL")
        self.assertEqual(len(self.llm.chamadas), 3)  # 2 blocos + síntese
        self.assertEqual(self.client.post("/llm/resumo", json={"texto": "curto"}).status_code, 422)

    def test_resumo_dados_template_mais_interpretacao(self):
        self.llm.saidas = ["Há concentração em poucos meses. Verifique as lacunas."]
        j = self.client.post("/llm/resumo-dados", json={"uf": "SP"}).json()
        self.assertIn("**Destaques:**", j["destaques"])
        self.assertIn("Interpretação (IA)", j["resumo"])
        self.assertEqual(j["total_registros"], 46795)

    def test_resumo_dados_descarta_interpretacao_com_numeros(self):
        self.llm.saidas = ["Teve 50 doses.", "Ainda 7 doses."]
        j = self.client.post("/llm/resumo-dados", json={}).json()
        self.assertIsNone(j["interpretacao"])
        self.assertNotIn("Interpretação (IA)", j["resumo"])  # só o template
        self.assertEqual(len(self.llm.chamadas), 2)  # 2 tentativas

    def test_resumo_dados_filtros_invalidos(self):
        self.assertEqual(self.client.post("/llm/resumo-dados", json={"uf": "ZZ"}).status_code, 400)
        r = self.client.post("/llm/resumo-dados", json={"data_inicio": str(date(2025, 5, 1)), "data_fim": "2025-01-01"})
        self.assertEqual(r.status_code, 400)

    def test_pergunta_dados_verifica_numeros(self):
        self.llm.saidas = ["SP tem 46.795 doses."]
        j = self.client.post("/llm/pergunta-dados", json={"pergunta": "Qual UF lidera?", "uf": "SP"}).json()
        self.assertEqual(j["numeros_nao_verificados"], [])
        self.assertIn("46.795", j["contexto"])
        self.llm.saidas = ["SP tem 99.999 doses."]
        j = self.client.post("/llm/pergunta-dados", json={"pergunta": "Qual UF lidera?", "uf": "SP"}).json()
        self.assertEqual(j["numeros_nao_verificados"], ["99.999"])

    def test_dica_saude_sempre_traz_aviso(self):
        self.llm.saidas = ["Tome a vacina da gripe. Procure um serviço de saú"]
        # generate_health_tip usa _chat; a rota anexa o aviso por código
        j = self.client.post("/llm/dica-saude", json={"query": "vacinas para idosos"}).json()
        self.assertTrue(j["dica"].endswith(summarizer.AVISO_DICA))
        self.assertTrue(j["dica"].startswith("Tome a vacina da gripe."))

    def test_historico_registrado(self):
        self.llm.saidas = ["ok"]
        self.client.post("/llm/pergunta-dados", json={"pergunta": "Qual UF lidera?", "destaques": "**Panorama:** x"})
        self.assertTrue(summarizer.HISTORICO_PATH.exists())
        self.assertIn("pergunta_dados", summarizer.HISTORICO_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
