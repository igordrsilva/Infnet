import streamlit as st
import pandas as pd

def match(competitions_df: pd.DataFrame, matches_df: pd.DataFrame, players_df: pd.DataFrame) -> None:
    # =======================================
    # FILTRO DAS PARTIDAS
    # =======================================
    form = st.form()
    with form:
        st.text_input('Competição', competitions_df['competition_name'].unique())

    # =======================================
    # EXIBIÇÃO DOS DADOS DA PARTIDA
    # =======================================
