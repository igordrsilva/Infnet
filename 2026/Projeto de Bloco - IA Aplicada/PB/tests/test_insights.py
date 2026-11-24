import unittest

import pandas as pd

from src.insights import age_bands, build_highlights, monthly_counts, top_counts


def _df():
    return pd.DataFrame(
        {
            "data_vacina": ["2025-01-10 00:00:00-03"] * 6 + ["2025-03-05 00:00:00-03"] * 2 + ["2025-06-01 00:00:00-03"],
            "sigla_uf_estabelecimento": ["SP"] * 5 + ["MG"] * 3 + ["RJ"],
            "nome_municipio_estabelecimento": ["Santos"] * 9,
            "descricao_vacina_fabricante": ["Pfizer"] * 6 + ["Moderna"] * 3,
            "numero_idade_paciente": [2, 5, 30, 65, 70, 8, 40, 11, 90],
            "tipo_sexo_paciente": ["F"] * 9,
        }
    )


class InsightsTest(unittest.TestCase):
    def test_highlights_numeros_exatos(self):
        h = build_highlights(_df())
        self.assertIn("9 doses aplicadas", h)
        self.assertIn("SP 5 (55,6%)", h)  # 5/9
        self.assertIn("Pfizer 6 (66,7%)", h)
        self.assertIn("01/2025 (6, 66,7% do total)", h)
        self.assertIn("cobertura vacinal", h)  # aviso fixo de limitação

    def test_highlights_apontam_meses_fracos_incluindo_sem_registro(self):
        h = build_highlights(pd.concat([_df()] * 200, ignore_index=True).assign(
            data_vacina=lambda d: d["data_vacina"]
        ))
        self.assertIn("02/2025 (0)", h)  # mês sem nenhum registro entra na lista

    def test_highlights_uma_uf_lista_municipios(self):
        h = build_highlights(_df()[lambda d: d["sigla_uf_estabelecimento"] == "SP"])
        self.assertIn("Municípios de SP", h)

    def test_highlights_vazio(self):
        self.assertIn("Nenhum registro", build_highlights(_df().iloc[0:0]))

    def test_series_dos_graficos(self):
        df = _df()
        meses = monthly_counts(df)
        self.assertEqual(list(meses.index), ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06"])
        self.assertEqual(int(meses.sum()), len(df))
        self.assertEqual(int(meses["2025-02"]), 0)
        self.assertEqual(int(age_bands(df).sum()), len(df))
        self.assertEqual(top_counts(df, ["sigla_uf_estabelecimento"], 1).index[0], "SP")


if __name__ == "__main__":
    unittest.main()
