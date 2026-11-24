import streamlit as st

from src.llm_client import LLMError, resumir_noticia


def news_card(title: str, text: str, url: str, container=None, key: str = ""):
    if container is None:
        container = st

    with container.container():
        container.subheader(title)

        resumo = text[:300]

        if len(text) > 300:
            resumo += "..."

        container.write(resumo)

        col_link, col_ia = container.columns(2)
        col_link.link_button("Ler notícia", url)

        state_key = f"resumo_ia_{key}"
        if col_ia.button("Resumir com IA", key=f"btn_{state_key}"):
            with st.spinner("Gerando resumo com a LLM local..."):
                try:
                    st.session_state[state_key] = resumir_noticia(title, text)
                except LLMError as e:
                    st.session_state.pop(state_key, None)
                    container.error(str(e))

        resultado = st.session_state.get(state_key)
        if resultado:
            container.info(resultado["resumo"])
            container.caption(
                f"Gerado por {resultado['modelo']} em {resultado['tempo_geracao_segundos']} s "
                f"({resultado.get('blocos_processados', 1)} bloco(s)). "
                "Resumo automático: confira o texto original."
            )

        container.divider()
