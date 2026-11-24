import unittest

import pandas as pd

from src.preprocessing import (
    fill_missing_values,
    normalize_values,
    remove_duplicates_and_outliers,
)


def _df():
    return pd.DataFrame(
        {
            "nome_pais_paciente": [None, "BRASIL", "BRASIL", "BRASIL"],
            "descricao_tipo_estabelecimento": ["UBS", None, "UBS", "UBS"],
            "nome_uf_paciente": [None, "SAO PAULO", "SAO PAULO", "SAO PAULO"],
            "nome_uf_estabelecimento": ["MINAS GERAIS", "SAO PAULO", "SAO PAULO", "SAO PAULO"],
            "descricao_local_aplicacao": ["Braco", "Braco", None, "Braco"],
            "descricao_vacina_fabricante": ["PFIZER BIONTECH", "Butantam", None, "FIO CRUZ"],
            "nome_municipio_paciente": [None, "SANTOS", "SANTOS", "SANTOS"],
            "nome_municipio_estabelecimento": ["BELO HORIZONTE", "SANTOS", "SANTOS", "SANTOS"],
            "descricao_condicao_maternal": [None, None, "Gestante", None],
            "sigla_uf_paciente": [None, "SP", "SP", "SP"],
            "sigla_uf_estabelecimento": ["MG", "SP", "SP", "SP"],
            "nome_etnia_indigena_paciente": [None, "XAVANTE", None, None],
            "nome_raca_cor_paciente": ["BRANCA", "PARDA", "PARDA", "PARDA"],
            "numero_idade_paciente": [30, 200, 5, 5],
        }
    )


class PreprocessingTest(unittest.TestCase):
    def test_fill_missing_values_nao_deixa_nulos(self):
        out = fill_missing_values(_df())
        self.assertEqual(int(out.isna().sum().sum()), 0)
        self.assertEqual(len(out), 4)  # nenhuma linha descartada por causa de ausentes

    def test_regras_de_imputacao(self):
        out = fill_missing_values(_df())
        self.assertEqual(out.loc[0, "nome_pais_paciente"], "BRASIL")
        self.assertEqual(out.loc[0, "sigla_uf_paciente"], "MG")  # copiada do estabelecimento
        self.assertEqual(out.loc[0, "nome_municipio_paciente"], "BELO HORIZONTE")
        self.assertEqual(out.loc[0, "nome_etnia_indigena_paciente"], "NÃO INDÍGENA")
        self.assertEqual(out.loc[0, "descricao_condicao_maternal"], "Não informado")
        self.assertEqual(out.loc[1, "descricao_tipo_estabelecimento"], "UBS")  # moda

    def test_remove_duplicatas_e_idades_implausiveis(self):
        out = remove_duplicates_and_outliers(_df().pipe(fill_missing_values))
        self.assertEqual(out["numero_idade_paciente"].max(), 30)  # 200 removida
        self.assertEqual(int(out.duplicated().sum()), 0)

    def test_normalizacao_de_fabricantes(self):
        out = normalize_values(fill_missing_values(_df()))
        fabricantes = set(out["descricao_vacina_fabricante"])
        self.assertIn("Pfizer", fabricantes)
        self.assertIn("Instituto Butantan", fabricantes)  # grafia "Butantam" unificada


if __name__ == "__main__":
    unittest.main()
