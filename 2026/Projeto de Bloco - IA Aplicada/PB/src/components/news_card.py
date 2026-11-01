import streamlit as st


def news_card(title: str, text: str, url: str, container=None):
    if container is None:
        container = st

    with container.container():
        container.subheader(title)

        resumo = text[:300]

        if len(text) > 300:
            resumo += "..."

        container.write(resumo)

        container.link_button("Ler notícia", url)
        container.divider()
