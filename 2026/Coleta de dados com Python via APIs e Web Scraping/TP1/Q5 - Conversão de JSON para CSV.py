import pandas as pd

""""
## Conversão de JSON para CSV
Escreva um programa Python que leia o arquivo dados_produtos.json (gerado no exercício 4) e converta os dados para um arquivo CSV chamado produtos.csv, com uma coluna para cada campo do produto (id, nome, preco, quantidade). 
Garanta que o cabeçalho do CSV corresponda exatamente aos nomes dos campos e que todos os 50 produtos estejam presentes no arquivo final.
"""

def convert_json_to_csv(json_path:str) -> None:
    """
    Lê um arquivo JSON e converte o conteúdo para um arquivo CSV.

    Args:
        json_path (str): Caminho para o arquivo JSON que será lido.
    """
    df = pd.read_json(json_path)

    df.to_csv(r'igor_silva_DR2_TP1/data/produtos.csv', index=False)


convert_json_to_csv(r'igor_silva_DR2_TP1/data/dados_produtos.json')
print(f'O arquivo produtos.csv foi salvo com sucesso!')