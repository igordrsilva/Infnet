import unittest

from llm import summarizer


class SummarizerTest(unittest.TestCase):
    def test_chunk_text_respeita_limites(self):
        texto = ("Frase de teste. " * 300 + "\n") * 10
        blocos = summarizer.chunk_text(texto, chunk_chars=6000, max_chars=12000)
        self.assertLessEqual(sum(len(b) for b in blocos), 12000 + 10)
        self.assertTrue(all(len(b) <= 6600 for b in blocos))
        self.assertEqual(summarizer.chunk_text(""), [])

    def test_chunk_text_curto_vira_um_bloco(self):
        self.assertEqual(summarizer.chunk_text("Texto curto."), ["Texto curto."])

    def test_limpar_interpretacao_remove_frases_com_numeros_e_cortadas(self):
        bruto = "Há concentração em maio, com mais de 50% das doses. O perfil é jovem. A série é irreg"
        self.assertEqual(summarizer.limpar_interpretacao(bruto), "O perfil é jovem.")
        self.assertEqual(summarizer.limpar_interpretacao("Só 1 frase com 2 números."), "")

    def test_numeros_nao_verificados(self):
        ref = "223.625 doses; 20,9%; 05/2025 (114.867)"
        self.assertEqual(summarizer.numeros_nao_verificados("SP tem 20,9% de 223.625.", ref), [])
        self.assertEqual(summarizer.numeros_nao_verificados("Foram 62,3% jovens.", ref), ["62,3"])
        self.assertEqual(summarizer.numeros_nao_verificados("1. item e 2. item", ref), [])  # marcadores

    def test_finalizar_dica_corta_fragmento_e_anexa_aviso(self):
        out = summarizer.finalizar_dica("Vacine-se contra a gripe e a covid todo ano. Consulte um profissional de saú")
        self.assertTrue(out.startswith("Vacine-se contra a gripe e a covid todo ano."))
        self.assertNotIn("saú", out.split("\n\n")[0])
        self.assertTrue(out.endswith(summarizer.AVISO_DICA))
        completo = summarizer.finalizar_dica("Texto completo.")
        self.assertTrue(completo.startswith("Texto completo.\n\n"))


if __name__ == "__main__":
    unittest.main()
