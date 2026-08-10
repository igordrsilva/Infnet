import pandas as pd

""""
## Manipulação de JSON
Crie um arquivo JSON chamado dados_produtos.json contendo uma lista de 50 produtos fictícios, cada um com os campos id (inteiro), nome (texto), preco (número decimal) e quantidade (inteiro). 
Escreva um programa Python que leia este arquivo e imprima na tela de forma estruturada (tabela).
"""

def read_json_file(path:str) -> pd.DataFrame:
    """
    Lê um arquivo JSON e retorna seu conteúdo como um DataFrame do pandas.

    Args:
        path (str): Caminho para o arquivo JSON que será lido.

    Returns:
        pd.DataFrame: DataFrame contendo os dados carregados do arquivo JSON.
    """
    df = pd.read_json(path)
    return df


df = read_json_file(r'igor_silva_DR2_TP1/data/dados_produtos.json')

print('='*50)
print(df.head(10))
print('='*50)