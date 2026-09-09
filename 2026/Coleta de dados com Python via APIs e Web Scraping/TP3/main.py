from src.data import *
import pandas as pd
import dotenv
import os

dotenv.load_dotenv()

URL_BOOKS = os.getenv('URL_BOOKS')

if __name__ == '__main__':
    soup = get_html_page(URL_BOOKS)
    df = pd.DataFrame(extract_main_info_from_books(soup))
    print(df.head())
    df.to_excel('catalogo_fornecedor.xlsx')