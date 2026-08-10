import pandas as pd

""""
## Manipulação de Dados Tabulares com CSV
Crie um arquivo CSV chamado dados_alunos.csv com as colunas nome, idade, curso. Preencha o arquivo com dados fictícios de pelo menos 12 alunos, distribuídos em 3 cursos distintos, sendo que um dos cursos deve ser “Ciência de Dados”. Use idades plausíveis para alunos de graduação. 
Escreva um programa Python que leia o arquivo, imprima os dados todos os alunos e verifique o tipo de dados de todas as colunas.
"""

def read_csv_file(path:str) -> pd.DataFrame:
    """
    Lê um arquivo CSV e retorna seu conteúdo como um DataFrame do pandas.

    Args:
        path (str): Caminho para o arquivo CSV que será lido.

    Returns:
        pd.DataFrame: DataFrame contendo os dados carregados do arquivo CSV.
    """
    df = pd.read_csv(path)
    return df


df = read_csv_file(r'igor_silva_DR2_TP1/data/dados_alunos.csv')

print('='*50)
print(df)
print('='*50)