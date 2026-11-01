import os

import pandas as pd
import streamlit as st

from src.ingesting import *
from src.preprocessing import *
from src.scraping import extract_news


@st.cache_data
def load_data():
    """
    Carrega e processa os dados de vacinação.
    """

    processed_path = "data/processed/processed_data.csv"
    raw_path = "data/raw/data.csv"

    if not os.path.exists(processed_path):
        if not os.path.exists(raw_path):
            get_raw_data()

        raw_df = pd.read_csv(raw_path)

        df = drop_unnecessary_columns(raw_df)
        df = fill_missing_values(df)
        df = normalize_values(df)

        os.makedirs(os.path.dirname(processed_path), exist_ok=True)

        export_processed_data(df, processed_path)

    return pd.read_csv(processed_path)


@st.cache_data
def load_news():
    """
    Carrega as notícias extraídas do blog.
    """
    news = extract_news()

    if news is None:
        return pd.read_csv("data/medicalway_news.csv")

    return pd.DataFrame(news, columns=["title", "url", "text"])
