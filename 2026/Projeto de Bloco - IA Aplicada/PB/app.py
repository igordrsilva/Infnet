import streamlit as st

st.set_page_config(
    page_title="Saúde e Bem-Estar",
    page_icon="⛑️",
    layout="wide",
    initial_sidebar_state="expanded",
)

noticias = st.Page("./src/pages/noticias.py", title="Notícias", icon="🏠")
vacinas = st.Page("./src/pages/vacinas.py", title="Vacinas", icon="💉")
dados = st.Page("./src/pages/dados.py", title="Base de dados", icon="📊")

pg = st.navigation({"Páginas": [noticias, vacinas], "Base de dados": [dados]})

st.title("ODS 3 - Saúde e Bem-Estar")
st.subheader("Objetivos de Desenvolvimento Sustentável")

st.write("""
Explore as diferentes páginas da aplicação para visualizar
indicadores, analisar dados, consultar a base de dados e
acompanhar notícias relacionadas à saúde.
""")

st.divider()

pg.run()
