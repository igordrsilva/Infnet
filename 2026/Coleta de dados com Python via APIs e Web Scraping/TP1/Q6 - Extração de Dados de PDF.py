from PyPDF2 import PdfReader
# O PyPDF2 é compatível com versões do python de 3.6 até 3.11. Tive que trocar o interpretador Python para funcionar.

"""
## Extração de Dados de PDF
Baixe a ata do Copom de junho de 2024, disponível em https://www.bcb.gov.br/publicacoes/atascomef/202406. Escreva um programa Python usando a biblioteca PyPDF2 (classe PdfReader) que percorra todas as páginas do PDF, extraia o texto de cada uma e imprima o texto completo no console.
"""

arquivo_pdf = r"data/Ata_57_Comef_pt.pdf"

reader = PdfReader(arquivo_pdf)
texto_completo = ""

for i, pagina in enumerate(reader.pages):
    texto_da_pagina = pagina.extract_text()
    texto_completo += f"\n--- PÁGINA {i + 1} ---\n" + texto_da_pagina

print(texto_completo)