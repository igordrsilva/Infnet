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
ciclo = st.Page("./src/pages/ciclo.py", title="Ciclo de Dados e IA", icon="🤖", default=True)

pg = st.navigation({"Visão geral": [ciclo], "Páginas": [noticias, vacinas], "Base de dados": [dados]})

st.title("ODS 3 - Saúde e Bem-Estar")
st.subheader("Objetivos de Desenvolvimento Sustentável")

st.write("""
Explore o ciclo completo de ciência de dados (coleta, preparação, análise e IA),
visualize indicadores de vacinação, consulte a base de dados e acompanhe
notícias de saúde, com resumos e respostas geradas por uma LLM local.
""")

st.divider()

pg.run()
