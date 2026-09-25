import streamlit as st
import pandas as pd

from pages.sidebar import sidebar

def players(competitions_df: pd.DataFrame, matches_df: pd.DataFrame, players_df: pd.DataFrame) -> None:
    st.session_state["current_page"] = "player"
    st.title("Jogadores")

    # =======================================
    # SIDEBAR
    # =======================================
    sidebar(competitions_df, matches_df, players_df)


competitions_df = st.session_state["competitions_df"]
matches_df = st.session_state["matches_df"]
players_df = st.session_state["players_df"]
players(competitions_df, matches_df, players_df)