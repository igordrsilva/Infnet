import pandas as pd
import plotly.express as px
# import matplotlib.pyplot as plt
import streamlit as st

def plot_table():
    pass


def plot_horizontal_bars(df: pd.DataFrame, x: str, y: str, labels: dict, title: str) -> None:
    fig = px.bar(
        df, 
        x = "goals",
        y = "team",
        orientation='h',
        labels = labels,
        title = title
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_pie():
    pass


def plot_graph(df: pd.DataFrame, x: str, y: str, labels: dict, title: str) -> None:
    fig = px.line(
        df, 
        x = x,
        y = y, 
        markers=True, 
        labels = labels,
        title = title
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_metrics(title: str, main_data: any, delta: any = None, delta_color: bool = False) -> None:
    if delta_color:
        st.metric(title, main_data, delta=delta, border=True)
    else:
        st.metric(title, main_data, delta=delta, delta_color="off", border=True)