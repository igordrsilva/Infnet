import os
import pandas as pd
import streamlit as st

from core.extract_data import *
from core.utils import *
from pages.match import *


# =======================================
# CONFIGURAÇÕES DA PÁGINA
# =======================================
st.set_page_config(
    page_title="Sport Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =======================================
# CARREGAMENTO DOS DADOS
# =======================================
@st.cache_data(ttl=3600)
def load_competitions():
    if "competitions_df" not in st.session_state:
        competitions_df = extract_competitions_info()
        st.session_state.df = competitions_df.copy()

    return competitions_df

@st.cache_data(ttl=3600)
def load_matches(competitions_df: pd.DataFrame):
    if "matches_df" not in st.session_state:
        matches_df = extract_matches_info(competitions_df)
        st.session_state.df = matches_df.copy()

    return matches_df

@st.cache_data(ttl=3600)
def load_players(players_df: pd.DataFrame):
    if "players_df" not in st.session_state:
        players_df = extract_players_info(players_df)
        st.session_state.df = players_df.copy()

    return players_df


competitions_df = load_competitions()
matches_df = load_matches(competitions_df)
players_df = load_players(matches_df)


# =======================================
# INFORMAÇÕES E GRÁFICOS DAS PARTIDAS
# =======================================

match(competitions_df, matches_df, players_df)