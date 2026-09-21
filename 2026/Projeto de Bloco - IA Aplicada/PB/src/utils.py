import pandas as pd


def find_column(df:pd.DataFrame, possible_names:list) -> str | None:
    """
    Procura uma coluna no DataFrame utilizando uma lista
    de possíveis nomes.

    Retorna o primeiro nome encontrado.
    Caso nenhuma coluna seja encontrada, retorna None.
    """

    for column in possible_names:
        if column in df.columns:
            return column

    return None


def convert_to_numeric(series:pd.Series) -> pd.Series:
    """
    Converte uma Series para valores numéricos.


    Valores que não puderem ser convertidos serão tratados
    como NaN.
    """

    return pd.to_numeric(
        series,
        errors="coerce"
    )