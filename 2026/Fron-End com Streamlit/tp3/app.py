import streamlit as st
import pandas as pd
import plotly.express as px
from time import sleep

st.set_page_config(page_title="Turistas por continentes - RJ", layout="wide")

@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def load_data(file:any) -> pd.DataFrame:
    df = pd.read_excel(file, skiprows=7)
    df.drop([0, 5, 6, 10, 11, 15, 28, 33, 52, 53, 56, 60], inplace=True)
    df.columns = ['País', 'Total','Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    df.drop('Total', axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df = df.iloc[:50,:]
    df['País'].str.strip()
    df.replace('-', 0, inplace=True)
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def plot_tourists_by_continent(df: pd.DataFrame) -> None:
    df_grouped = df.groupby(['Continente', 'Ano'])['Total'].sum().reset_index()
    fig = px.line(df_grouped, x='Ano', y='Total', color='Continente', markers=True,
                  title="Número de turistas por continente ao longo dos anos")
    fig.update_layout(xaxis_title="Ano", yaxis_title="Número de turistas")
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    st.title("Turistas por continentes - RJ")
    st.write("Vindos por via aérea")

    st.sidebar.title("Objetivo do Dashboard")
    st.sidebar.write("""
    Este dashboard tem como objetivo apresentar informações sobre o número de turistas que visitam o estado do Rio de Janeiro, vindos por via aérea, categorizados por países e continentes.
    """)
    
    st.sidebar.markdown("---")

    uploaded_file = st.sidebar.file_uploader(
        "Upload do arquivo XLSX",
        type=["xls", "xlsx"]
    )

    if uploaded_file is not None:
        arquivo_novo = (
            st.session_state.get("nome_arquivo") != uploaded_file.name
        )

        if arquivo_novo:

            st.session_state["nome_arquivo"] = uploaded_file.name

            spinner_placeholder = st.empty()
            progress_placeholder = st.empty()

            with spinner_placeholder.container():
                with st.spinner("Carregando dados..."):

                    barra = progress_placeholder.progress(
                        0,
                        text="Iniciando o processo..."
                    )

                    for percentual in range(100):
                        sleep(0.05)

                        barra.progress(
                            percentual + 1,
                            text=f"Progresso: {percentual + 1}%"
                        )

                    st.session_state["df"] = load_data(uploaded_file)

            spinner_placeholder.empty()
            progress_placeholder.empty()

    if "df" in st.session_state:
        df = st.session_state["df"]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            filter_enabled = st.checkbox(
                "Ativar filtros",
                value=False
            )

        with col2:
            selected_months = st.multiselect(
                "Selecione o mês",
                df.columns[1:],
                default=df.columns[1:],
                disabled=not filter_enabled
            )

        with col3:
            selected_country = st.selectbox(
                "Selecione o país",
                df["País"].unique(),
                disabled=not filter_enabled
            )

        with col4:
            show_columns = st.radio(
                "Exibir nomes das colunas",
                ["Sim", "Não"],
                index=0,
                horizontal=True,
                disabled=not filter_enabled
            )

        if filter_enabled:
            df_filtrado = df[
                df["País"] == selected_country
            ][["País"] + selected_months]

        else:
            df_filtrado = df.copy()

        if show_columns == "Sim":
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.table(
                df_filtrado,
                hide_index=True,
                hide_header=True
            )

        st.sidebar.download_button(
            label="Download do arquivo filtrado",
            data=df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name="turistas_filtrados.csv",
            mime="text/csv"
        )

        st.sidebar.markdown("---")
        col1, col2 = st.sidebar.columns(2)
        col1.background_color = st.sidebar.color_picker("Cor de fundo", "#f0f0f0")
        col2.text_color = st.sidebar.color_picker("Cor do texto", "#000000")

        st.markdown(
            f"""
            <style>
                .stApp {{
                    background-color: {col1.background_color};
                    color: {col2.text_color};
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
    
        # Gráficos básicos
        col1, col2, col3 = st.columns(3)

        df_top10 = df_filtrado.copy()

        # Soma dos turistas de todos os meses para cada país
        df_top10["Total"] = df_top10[selected_months].sum(axis=1)

        # Seleciona os 10 países com maior número de turistas
        df_top10 = (
            df_top10
            .nlargest(10, "Total")
            .drop(columns="Total")
        )

        # Gráfico de barras
        fig_bar = px.bar(
            df_top10,
            x="País",
            y=selected_months,
            title="Turistas por país"
        )

        col1.plotly_chart(
            fig_bar,
            use_container_width=True
        )


        # Gráfico de linhas
        df_linha = df_top10.melt(
            id_vars="País",
            var_name="Mês",
            value_name="Turistas"
        )

        fig_line = px.line(
            df_linha,
            x="Mês",
            y="Turistas",
            color="País",
            markers=True,
            title="Evolução de turistas por mês"
        )

        col2.plotly_chart(
            fig_line,
            use_container_width=True
        )


        # Gráfico de pizza
        df_pizza = df_top10.melt(
            id_vars="País",
            var_name="Mês",
            value_name="Turistas"
        )

        df_pizza = (
            df_pizza
            .groupby("País")["Turistas"]
            .sum()
            .reset_index()
        )

        fig_pie = px.pie(
            df_pizza,
            names="País",
            values="Turistas",
            title="Participação por país"
        )

        col3.plotly_chart(
            fig_pie,
            use_container_width=True
        )
        

        # Gráficos avançados
        col1, col2 = st.columns([1, 1])

        df_avancado = df_top10.copy()
        df_avancado["Total"] = df_avancado[selected_months].sum(axis=1)

        fig_hist = px.histogram(
            df_avancado,
            x="Total",
            nbins=10,
            title="Distribuição do número de turistas",
            labels={
                "Total": "Total de turistas"
            }
        )

        fig_hist.update_layout(
            xaxis_title="Total de turistas",
            yaxis_title="Quantidade de países"
        )

        col1.plotly_chart(
            fig_hist,
            use_container_width=True
        )

        if len(selected_months) >= 2:

            mes_x = selected_months[0]
            mes_y = selected_months[1]

            fig_scatter = px.scatter(
                df_avancado,
                x=mes_x,
                y=mes_y,
                text="País",
                size="Total",
                hover_name="País",
                title=f"Relação entre {mes_x} e {mes_y}"
            )

            fig_scatter.update_traces(
                textposition="top center"
            )

            fig_scatter.update_layout(
                xaxis_title=f"Turistas em {mes_x}",
                yaxis_title=f"Turistas em {mes_y}"
            )

            col2.plotly_chart(
                fig_scatter,
                use_container_width=True
            )

        else:

            col2.warning(
                "Selecione pelo menos dois meses para visualizar o scatter plot."
            )


        col1, col2, col3 = st.columns(3)

        qtd_paises = df_filtrado["País"].nunique()
        total_turistas = df_filtrado[selected_months].sum().sum()
        media_turistas = (
            df_filtrado[selected_months]
            .sum(axis=1)
            .mean()
        )

        with col1:
            st.metric(
                label="Países",
                value=qtd_paises
            )

        with col2:
            st.metric(
                label="Total de turistas",
                value=f"{total_turistas:,.0f}".replace(",", ".")
            )

        with col3:
            st.metric(
                label="Média de turistas por país",
                value=f"{media_turistas:,.0f}".replace(",", ".")
            )