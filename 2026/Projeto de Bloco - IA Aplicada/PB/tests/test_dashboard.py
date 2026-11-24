import os
import unittest
from pathlib import Path
from unittest import mock

import src.llm_client as lc

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "data/processed/processed_data.csv"


def _post(rota, payload):
    if rota == "/llm/pergunta-dados":
        return {"resposta": "SP lidera.", "modelo": "m", "tempo_geracao_segundos": 1.0, "contexto": "c", "numeros_nao_verificados": ["99.999"]}
    if rota == "/llm/resumo-dados":
        return {"resumo": "r", "interpretacao": "INTERP", "modelo": "m", "tempo_geracao_segundos": 1.0}
    return {"resumo": "RES NOT", "modelo": "m", "tempo_geracao_segundos": 1.0, "blocos_processados": 2}


@unittest.skipUnless(ARQ.exists(), "base processada ausente")
class DashboardTest(unittest.TestCase):
    def setUp(self):
        os.chdir(RAIZ)  # as páginas usam caminhos relativos a data/
        self.p1 = mock.patch.object(lc, "_post", side_effect=_post)
        self.p2 = mock.patch.object(lc, "status_ia", return_value={"online": True, "pronto": True, "modelo": "Qwen"})
        self.p1.start()
        self.p2.start()
        from streamlit.testing.v1 import AppTest

        self.at = AppTest.from_file(str(RAIZ / "src/pages/ciclo.py"), default_timeout=180).run()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def test_renderiza_sem_excecoes_com_4_abas(self):
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(len(self.at.tabs), 4)

    def test_filtro_por_uf_altera_o_recorte(self):
        self.at.selectbox[0].select("SP").run()
        valores = [m.value for m in self.at.metric if m.label == "Doses no recorte"]
        self.assertEqual(valores, ["46.795"])

    def test_interpretacao_por_ia(self):
        next(b for b in self.at.button if b.label.startswith("Gerar interpretação")).click().run()
        self.assertTrue(any("INTERP" in i.value for i in self.at.info))

    def test_chat_sinaliza_numeros_nao_verificados(self):
        self.at.chat_input[0].set_value("Qual UF lidera?").run()
        self.assertTrue(any("99.999" in w.value for w in self.at.warning))

    def test_api_offline_mostra_erro_na_barra_lateral(self):
        with mock.patch.object(lc, "status_ia", return_value={"online": False, "pronto": False, "modelo": None}):
            from streamlit.testing.v1 import AppTest

            at = AppTest.from_file(str(RAIZ / "src/pages/ciclo.py"), default_timeout=180).run()
        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any("offline" in e.value for e in at.sidebar.error))


if __name__ == "__main__":
    unittest.main()
