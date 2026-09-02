from src.ingesting import get_raw_data
from src.preprocessing import drop_unnecessary_columns, fill_missing_values, normalize_values, export_processed_data
import pandas as pd
import os 
import streamlit as st


if __name__ == "__main__":
    if not os.path.exists("data/raw/data.csv"):
        get_raw_data()

    raw_df = pd.read_csv("data/raw/data.csv")
    df = drop_unnecessary_columns(raw_df)
    df = fill_missing_values(df)
    df = normalize_values(df)
    export_processed_data(df)
    
    df = pd.read_csv("data/processed_data.csv")

    st.set_page_config(page_title="Painel de vacinação - Brasil", page_icon=":syringe:", layout="wide")
    st.title("Painel de vacinação - Brasil")
    st.write("Este é o painel de vacinação do Brasil.")
    
    st.write("Raw data:")
    st.dataframe(df.head(10))