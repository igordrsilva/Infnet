from bs4 import BeautifulSoup
import requests
import re

estrelas = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}

# 1. Busca o html da url informada
def get_html_page(url:str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"An error happened: {e}")
        return None

def extract_main_info_from_books(soup:str) -> list:
    if soup is None:
        return []
    
    livros = soup.find_all('article', class_='product_pod')
    books = []

    for livro in livros:
        infos = {}
        infos['title'] = livro.h3.a['title']
        price_raw = livro.find('p', class_='price_color').text
        price_numeric = re.sub(r'[^\d.]', '', price_raw)
        infos['price'] = float(price_numeric) if price_numeric else 0.0
        infos['availability'] = livro.find('p', class_='instock availability').text.strip()
        classes = livro.find('p', class_='star-rating').get('class', [])
        avaliacao = classes[1] if len(classes) > 1 else 'Zero'

        infos['star_rating'] = estrelas.get(avaliacao, 0)
        books.append(infos)

    return books