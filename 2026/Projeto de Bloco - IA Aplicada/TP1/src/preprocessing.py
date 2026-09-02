import pandas as pd
import numpy as np


def drop_unnecessary_columns(df:pd.DataFrame) -> pd.DataFrame:
    """
    Drop unnecessary columns from the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The DataFrame with unnecessary columns dropped.
    """
    columns_to_drop = ['Unnamed: 0','descricao_natureza_estabelecimento','codigo_via_administracao','codigo_origem_registro','codigo_pais_paciente','codigo_estrategia_vacinacao','descricao_origem_registro','data_entrada_rnds','codigo_troca_documento','nome_razao_social_estabelecimento','codigo_sistema_origem','status_documento','codigo_documento','codigo_municipio_estabelecimento','data_deletado_rnds','codigo_municipio_paciente','codigo_pais_origem','descricao_sistema_origem','descricao_troca_documento','descricao_via_administracao','numero_cep_paciente','nome_fantasia_estalecimento','codigo_etnia_indigena_paciente','codigo_local_aplicacao','codigo_lote_vacina','codigo_cnes_estabelecimento','codigo_tipo_estabelecimento','codigo_natureza_estabelecimento','codigo_raca_cor_paciente','codigo_vacina_grupo_atendimento','codigo_paciente','codigo_vacina_fabricante','codigo_condicao_maternal']
    
    df = df.drop(columns=columns_to_drop, errors='ignore')
    return df


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The DataFrame with missing values filled.
    """
    df['nome_pais_paciente'] = df['nome_pais_paciente'].fillna('BRASIL') # nome_pais_paciente
    df['descricao_tipo_estabelecimento'] = df['descricao_tipo_estabelecimento'].fillna(lambda x: x.mode()[0]) # descricao_tipo_estabelecimento
    df['nome_uf_paciente'] = df['nome_uf_paciente'].fillna(df['nome_uf_estabelecimento']) # nome_uf_paciente
    df['descricao_local_aplicacao'] = df['descricao_local_aplicacao'].fillna(lambda x: x.mode()[0]) # descricao_local_aplicacao
    df['descricao_vacina_fabricante'] = df['descricao_vacina_fabricante'].fillna(lambda x: x.mode()[0]) # descricao_vacina_fabricante
    df['nome_municipio_paciente'] = df['nome_municipio_paciente'].fillna(df['nome_municipio_estabelecimento']) # nome_municipio_paciente
    df['descricao_condicao_maternal'] = df['descricao_condicao_maternal'].fillna(lambda x: x.mode()[0]) # descricao_condicao_maternal
    df['sigla_uf_paciente'] = df['sigla_uf_paciente'].fillna(df['sigla_uf_estabelecimento']) # sigla_uf_paciente
    df['nome_etnia_indigena_paciente'] = df['nome_etnia_indigena_paciente'].fillna('NÃO INDÍGENA') # nome_etnia_indigena_paciente

    df.dropna(inplace=True)

    return df


def normalize_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize values in the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The DataFrame with normalized values.
    """
    df['nome_pais_paciente'] = df['nome_pais_paciente'].str.title() # nome_pais_paciente
    df['nome_raca_cor_paciente'] = df['nome_raca_cor_paciente'].str.title() # nome_raca_cor_paciente
    df['nome_municipio_estabelecimento'] = df['nome_municipio_estabelecimento'].str.title() # nome_municipio_estabelecimento
    df['descricao_tipo_estabelecimento'] = df['descricao_tipo_estabelecimento'].str.title() # descricao_tipo_estabelecimento
    df['nome_uf_paciente'] = df['nome_uf_paciente'].str.title() # nome_uf_paciente
    df['descricao_local_aplicacao'] = df['descricao_local_aplicacao'].str.title() # descricao_local_aplicacao

    condicoes = [
        df["descricao_vacina_fabricante"].str.contains("ASTRAZENECA", case=False, na=False),
        df["descricao_vacina_fabricante"].str.contains("CORONAVAC", case=False, na=False),
        df["descricao_vacina_fabricante"].str.contains("JANSSEN", case=False, na=False),
        df["descricao_vacina_fabricante"].str.contains("PFIZER", case=False, na=False),
        df["descricao_vacina_fabricante"].str.contains("MODERNA", case=False, na=False),
        (
            df["descricao_vacina_fabricante"].str.contains("BUTANTAN", case=False, na=False) | 
            df["descricao_vacina_fabricante"].str.contains("BUTANTAM", case=False, na=False)
        ),
        (
            df["descricao_vacina_fabricante"].str.contains("FIOCRUZ", case=False, na=False) | 
            df["descricao_vacina_fabricante"].str.contains("FIOCR UZ", case=False, na=False)
        ),
    ]

    resultados = [
        "ASTRAZENECA",
        "CORONAVAC",
        "JANSSEN",
        "PFIZER",
        "MODERNA",
        "INSTITUTO BUTANTAN",
        "FIOCRUZ",
    ]

    df["descricao_vacina_fabricante"] = np.select(
        condicoes, resultados, default=df["descricao_vacina_fabricante"]
    )

    df["descricao_vacina_fabricante"] = df["descricao_vacina_fabricante"].str.title()
    df["nome_municipio_paciente"] = df["nome_municipio_paciente"].str.title()
    df["descricao_condicao_maternal"] = df["descricao_condicao_maternal"].str.title()
    df["nome_uf_estabelecimento"] = df["nome_uf_estabelecimento"].str.title()
    df["nome_etnia_indigena_paciente"] = df["nome_etnia_indigena_paciente"].str.title()

    return df

def export_processed_data(df: pd.DataFrame) -> None:
    """
    Export the processed DataFrame to a CSV file.

    Parameters:
    df (pd.DataFrame): The processed DataFrame.
    output_path (str): The path where the CSV file will be saved.
    """
    df.to_csv('data/processed_data.csv', index=False)