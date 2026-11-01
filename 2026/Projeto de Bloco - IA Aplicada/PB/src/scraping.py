import os
from urllib.parse import urljoin, urlparse

import dotenv
import requests
from bs4 import BeautifulSoup

dotenv.load_dotenv()
API_NOTICIA = os.getenv("API_NOTICIA")
MAX_NEWS = 5


def get_html_page(url: str):
    """
    Acessa a URL e retorna o HTML usando BeautifulSoup.
    """
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})

        response.raise_for_status()
        response.encoding = response.apparent_encoding

        return BeautifulSoup(response.text, "html.parser")

    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return None


def extract_news():
    """
    Extrai os 5 primeiros conteúdos do blog da Medicalway.
    Retorna uma lista de dicionários.
    """
    soup = get_html_page(API_NOTICIA)

    if soup is None:
        return []

    news_list = []
    article_urls = []

    base_domain = urlparse(API_NOTICIA).netloc

    links = soup.select("a.ct-link-button[href]")

    print(f"Links encontrados na página: {len(links)}")

    for link in links:
        href = link.get("href", "").strip()
        link_text = link.get_text(" ", strip=True).upper()

        if link_text != "LEIA MAIS":
            continue

        if not href or href.startswith("#"):
            continue

        article_url = urljoin(API_NOTICIA, href)

        parsed_url = urlparse(article_url)

        if parsed_url.netloc.lower() != base_domain.lower():
            continue

        article_url = (
            parsed_url._replace(fragment="", query="").geturl().rstrip("/") + "/"
        )

        if article_url.rstrip("/") == API_NOTICIA.rstrip("/"):
            continue

        if article_url not in article_urls:
            article_urls.append(article_url)

        if len(article_urls) >= MAX_NEWS:
            break

    print(f"URLs de notícias identificadas: {len(article_urls)}")

    for article_url in article_urls:
        print(f"\nAcessando: {article_url}")

        article_soup = get_html_page(article_url)

        if article_soup is None:
            continue

        title_tag = article_soup.select_one("h1")

        title = title_tag.get_text(" ", strip=True) if title_tag else None

        content_tag = article_soup.select_one(
            ".entry-content, "
            ".post-content, "
            ".elementor-widget-theme-post-content, "
            ".ct-inner-content, "
            "main"
        )

        if content_tag is None:
            content_tag = article_soup.body

        content = ""

        if content_tag:
            for element in content_tag.select(
                "script, style, nav, header, footer, aside, form, iframe"
            ):
                element.decompose()

            paragraphs = content_tag.select("p, h2, h3, li")

            content = "\n".join(
                element.get_text(" ", strip=True)
                for element in paragraphs
                if element.get_text(" ", strip=True)
            )

        if title:
            news_list.append({"title": title, "url": article_url, "text": content})

            print(f"Notícia extraída: {title}")
            print(f"Caracteres extraídos: {len(content)}")

        else:
            print(f"Não foi possível extrair o título: {article_url}")

    print(f"\nTotal de notícias extraídas: {len(news_list)}")

    return news_list


if __name__ == "__main__":
    news = extract_news()

    for item in news:
        print(item["title"])
        print(item["url"])
        print(item["text"][:200])
        print("-" * 50)
