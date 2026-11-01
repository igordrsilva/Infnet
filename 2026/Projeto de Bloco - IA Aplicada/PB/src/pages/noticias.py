import streamlit as st

from src.components.news_card import news_card
from src.data_loader import load_news

st.title("Notícias")
st.write(
    "Acompanhe as principais notícias e novidades relacionadas à vacinação no Brasil. Nesta seção, você encontrará informações, atualizações e conteúdos relevantes sobre campanhas de imunização, saúde pública e avanços na área da vacinação."
)
st.divider()

df_news = load_news()

if df_news.empty:
    st.info("Nenhuma notícia disponível.")
else:
    col1, col2 = st.columns(2)

    for i, (_, noticia) in enumerate(df_news.iterrows()):
        col = col1 if i % 2 == 0 else col2

        news_card(
            title=noticia["title"],
            text=noticia["text"],
            url=noticia["url"],
            container=col,
        )
