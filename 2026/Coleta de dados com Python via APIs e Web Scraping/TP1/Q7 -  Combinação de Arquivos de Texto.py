

"""
Crie dois arquivos de texto, parte1.txt e parte2.txt, cada um contendo uma parte de uma história curta (mínimo de 3 a 5 linhas cada). Escreva um programa Python que leia os dois arquivos, na ordem correta, e combine o conteúdo em um único arquivo chamado historia_completa.txt, preservando as quebras de linha originais de cada parte.
"""

def read_and_export_full_history(path: str, file_name_1: str, file_name_2: str) -> None:
    with open(f'{path}/{file_name_1}', 'r', encoding='utf-8') as arquivo1:
        text_1 = arquivo1.read()

    with open(f'{path}/{file_name_2}', 'r', encoding='utf-8') as arquivo2:
        text_2 = arquivo2.read()

    history = f"""{text_1}\n\n{text_2}"""

    with open(f"{path}/historia_completa.txt", "w", encoding="utf-8") as arquivo:
        arquivo.write(history)

read_and_export_full_history(
    'igor_silva_DR2_TP1/data',
    'parte1.txt',
    'parte2.txt'
)