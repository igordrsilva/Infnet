from bs4 import BeautifulSoup
import requests
import re


def get_html_page(url: str):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    except requests.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None
    
def extract_news(soup) -> list:
    if soup is None:
        return []

    news = []

    textos = soup.select("div.comp-text p")

    for texto in textos:
        strong = texto.find("strong")

        if strong:
            titulo = strong.get_text(strip=True)

            strong.extract()

            descricao = texto.get_text(" ", strip=True)

            news.append({
                "title": titulo,
                "text": descricao
            })

    return news


# import dotenv
# import os

# dotenv.load_dotenv()
# API_NOTICIA = os.getenv("API_NOTICIA")

# soup = get_html_page(API_NOTICIA)
# extract_news(soup)