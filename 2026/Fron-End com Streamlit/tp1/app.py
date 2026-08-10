import streamlit as st # importação do pacote streamlit com alias st
import pandas as pd # importação do pacote pandas com alias pd
import kagglehub

# Carregando o dataset "Most Streamed Spotify Songs 2024" do Kaggle
path = kagglehub.dataset_download("nelgiriyewithana/most-streamed-spotify-songs-2024")
dataset_path = path + "/Most Streamed Spotify Songs 2024.csv"

st.title("TP1 - Desenvolvimento front-end com Streamlit")

st.header("Análise das músicas mais transmitidas no Spotify em 2024")
st.subheader("Explorando o dataset 'Most Streamed Spotify Songs 2024'")

st.text("Este aplicativo Streamlit apresenta uma análise das músicas mais transmitidas no Spotify em 2024. Utilizando o dataset fornecido, podemos explorar informações sobre os artistas, gêneros musicais e popularidade das músicas.")

st.markdown("O _dataset_ contém informações sobre as músicas mais transmitidas no _Spotify_ em 2024, incluindo o **nome da música**, **artista**, **gênero musical**, **número de streams** e **popularidade**. A seguir, apresentamos uma visão geral dos dados.")

st.write("Visualizando as primeiras linhas do dataset:")
df = pd.read_csv(dataset_path, encoding='latin-1')
st.dataframe(df.head())

st.write(f"Play the top 1 song: {df.iloc[0]['Track']} by {df.iloc[0]['Artist']}")
audio_file = open('files/million_dollar_baby-tommy_richman.mp3', 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format='audio/mp3')

st.write("Métricas do dataset:")
col1, col2, col3 = st.columns([1, 1, 2])
col1.metric("Número de músicas", df.shape[0])
col2.metric("Número de artistas", df['Artist'].nunique())
col3.metric("Artista mais popular no Spotify", df.groupby('Artist')['Spotify Streams'].sum().idxmax())

"## FAQ - Perguntas Frequentes"
artista_popular = df['Artist'].value_counts().idxmax()

"Quantas músicas o artista mais popular tem no Spotify?"
df[df['Artist'] == artista_popular]['Track'].count(), 'música(s)'

"Somados todas as músicas, quantos plays o artista mais popular tem?"
df[df['Artist'] == artista_popular]['Spotify Streams'].str.replace(',', '').astype(int).sum(), 'plays'