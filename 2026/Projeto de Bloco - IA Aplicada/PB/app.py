import os
import pandas as pd
import streamlit as st
import dotenv

from src.ingesting import *
from src.preprocessing import *
from src.utils import *
from src.scraping import *


dotenv.load_dotenv()
API_NOTICIA = os.getenv("API_NOTICIA")

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Painel de Vacinação - Brasil",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

@st.cache_data
def load_data():
    """
    Carrega e processa os dados.

    st.cache_data evita que o processamento seja executado
    novamente a cada interação do usuário.
    """

    if not os.path.exists("data/processed_data.csv"):
        if not os.path.exists("data/raw/data.csv"):

            get_raw_data()

        raw_df = pd.read_csv("data/raw/data.csv")
        df = drop_unnecessary_columns(raw_df)
        df = fill_missing_values(df)
        df = normalize_values(df)
        export_processed_data(df, 'data/processed_data.csv')

    return pd.read_csv("data/processed_data.csv")

df = load_data()


# ============================================================
# WEB SCRAPING
# ============================================================

@st.cache_data
def make_scrap():

    path = "data/news.csv"

    if os.path.exists(path) and os.path.getsize(path) > 0:
        return pd.read_csv(path)

    soup = get_html_page(API_NOTICIA)
    news = extract_news(soup)

    if not news:
        st.warning("Nenhuma notícia foi encontrada.")
        return pd.DataFrame(columns=["title", "text"])

    df = pd.DataFrame(news)

    export_processed_data(df, path)

    return df

df_news = make_scrap()


# ============================================================
# SESSION STATE
# ============================================================

if "df" not in st.session_state:
    st.session_state.df = df.copy()

df = st.session_state.df


# ============================================================
# IDENTIFICAÇÃO DAS COLUNAS
# ============================================================

date_column = find_column(
    df,
    [
        "data_vacina"
    ]
)

uf_column = find_column(
    df,
    [
        "sigla_uf_estabelecimento",
        "sigla_uf_paciente"
    ]
)

municipio_column = find_column(
    df,
    [
        "nome_municipio_estabelecimento",
        "nome_municipio_paciente"
    ]
)

vaccine_column = find_column(
    df,
    [
        "descricao_vacina_fabricante"
    ]
)

dose_column = find_column(
    df,
    [
        "codigo_dose_vacina"
    ]
)


# ============================================================
# PREPARAÇÃO DA DATA
# ============================================================

if date_column:
    df = df.copy()

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )


# ============================================================
# TÍTULO E DESCRIÇÃO
# ============================================================

st.title("Painel de Vacinação — Brasil")

st.subheader(
    "Monitoramento da vacinação e da Saúde Pública — ODS 3"
)

st.write(
    """
    Este dashboard apresenta informações sobre vacinação
    no Brasil, permitindo explorar a aplicação de doses
    por período, localização e vacina.

    Os filtros estão disponíveis na barra lateral e são
    aplicados somente após o clique em **Aplicar filtros**.
    """
)

st.divider()


# ============================================================
# SESSION STATE — FILTROS
# ============================================================

if "filtros_aplicados" not in st.session_state:
    st.session_state.filtros_aplicados = {
        "periodo": None,
        "ufs": [],
        "municipios": [],
        "vacinas": []
    }


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Filtros")
st.sidebar.write(
    "Selecione os filtros e clique em **Aplicar filtros**."
)

with st.sidebar.form("filtros_form"):
    if date_column:
        valid_dates = df[date_column].dropna()

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            periodo = st.date_input(
                "Período",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="filtro_periodo"
            )

        else:
            periodo = None

    else:
        periodo = None

    if uf_column:
        uf_options = sorted(
            df[uf_column]
            .dropna()
            .astype(str)
            .unique()
        )

        ufs = st.multiselect(
            "UF",
            options=uf_options,
            key="filtro_ufs"
        )

    else:
        ufs = []

    if municipio_column:
        municipio_options = sorted(
            df[municipio_column]
            .dropna()
            .astype(str)
            .unique()
        )

        municipios = st.multiselect(
            "Município",
            options=municipio_options,
            key="filtro_municipios"
        )

    else:
        municipios = []

    if vaccine_column:
        vaccine_options = sorted(
            df[vaccine_column]
            .dropna()
            .astype(str)
            .unique()
        )

        vacinas = st.multiselect(
            "Vacina",
            options=vaccine_options,
            key="filtro_vacinas"
        )

    else:
        vacinas = []

    aplicar = st.form_submit_button(
        "Aplicar filtros",
        use_container_width=True
    )

if aplicar:
    st.session_state.filtros_aplicados = {
        "periodo": periodo,
        "ufs": ufs,
        "municipios": municipios,
        "vacinas": vacinas
    }

filtros = st.session_state.filtros_aplicados

filtered_df = df.copy()

if (
    date_column
    and filtros["periodo"] is not None
    and len(filtros["periodo"]) == 2
):

    start_date, end_date = filtros["periodo"]

    filtered_df = filtered_df[
        (filtered_df[date_column].dt.date >= start_date)
        &
        (filtered_df[date_column].dt.date <= end_date)
    ]

if uf_column and filtros["ufs"]:

    filtered_df = filtered_df[
        filtered_df[uf_column]
        .astype(str)
        .isin(filtros["ufs"])
    ]

if municipio_column and filtros["municipios"]:

    filtered_df = filtered_df[
        filtered_df[municipio_column]
        .astype(str)
        .isin(filtros["municipios"])
    ]

if vaccine_column and filtros["vacinas"]:

    filtered_df = filtered_df[
        filtered_df[vaccine_column]
        .astype(str)
        .isin(filtros["vacinas"])
    ]

limpar_filtros = st.sidebar.button(
    "Limpar filtros",
    use_container_width=True
)

if limpar_filtros:
    st.session_state.filtros_aplicados = {
        "periodo": None,
        "ufs": [],
        "municipios": [],
        "vacinas": []
    }

    if "filtro_periodo" in st.session_state:
        del st.session_state["filtro_periodo"]

    if "filtro_ufs" in st.session_state:
        del st.session_state["filtro_ufs"]

    if "filtro_municipios" in st.session_state:
        del st.session_state["filtro_municipios"]

    if "filtro_vacinas" in st.session_state:
        del st.session_state["filtro_vacinas"]

    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("Filtros aplicados")

if filtros["periodo"]:
    periodo_aplicado = filtros["periodo"]
    
    if len(periodo_aplicado) == 2:
        st.sidebar.caption(
            f"Período: "
            f"{periodo_aplicado[0].strftime('%d/%m/%Y')} "
            f"até "
            f"{periodo_aplicado[1].strftime('%d/%m/%Y')}"
        )

if filtros["ufs"]:
    st.sidebar.caption(
        f"UF: {', '.join(filtros['ufs'])}"
    )

if filtros["municipios"]:
    st.sidebar.caption(
        f"Municípios selecionados: "
        f"{len(filtros['municipios'])}"
    )

if filtros["vacinas"]:
    st.sidebar.caption(
        f"Vacinas selecionadas: "
        f"{len(filtros['vacinas'])}"
    )

if not any([
    filtros["ufs"],
    filtros["municipios"],
    filtros["vacinas"]
]):

    st.sidebar.caption(
        "Nenhum filtro categórico aplicado."
    )

if filtered_df.empty:
    st.warning(
        "Nenhum registro foi encontrado para os filtros "
        "selecionados."
    )

    st.stop()


# ============================================================
# CÁLCULO DAS MÉTRICAS
# ============================================================

if dose_column:
    doses = convert_to_numeric(
        filtered_df[dose_column]
    )

    total_doses = doses.sum()

else:
    total_doses = len(filtered_df)


if uf_column:
    total_ufs = filtered_df[
        uf_column
    ].nunique()

else:
    total_ufs = 0


if municipio_column:
    total_municipios = filtered_df[
        municipio_column
    ].nunique()

else:
    total_municipios = 0


# ============================================================
# BIG NUMBERS
# ============================================================

st.subheader("Indicadores")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Doses aplicadas",
        f"{total_doses:,.0f}".replace(",", ".")
    )

with col2:
    st.metric(
        "Registros",
        f"{len(filtered_df):,.0f}".replace(",", ".")
    )

with col3:
    st.metric(
        "UFs",
        total_ufs
    )

with col4:
    st.metric(
        "Municípios",
        total_municipios
    )

st.divider()


# ============================================================
# GRÁFICO — EVOLUÇÃO TEMPORAL
# ============================================================

st.subheader("Evolução da vacinação")

if date_column and dose_column:
    temporal_df = filtered_df.copy()
    temporal_df["doses"] = convert_to_numeric(
        temporal_df[dose_column]
    )

    temporal_df = (
        temporal_df
        .groupby(date_column)["doses"]
        .sum()
        .sort_index()
    )

    st.line_chart(
        temporal_df
    )

else:
    st.info(
        "Não foi possível construir o gráfico temporal "
        "com as colunas disponíveis."
    )


col1, col2 = st.columns(2)

with col1:
    st.subheader("Doses por UF")

    if uf_column and dose_column:
        uf_df = filtered_df.copy()
        uf_df["doses"] = convert_to_numeric(uf_df[dose_column])

        uf_df = (
            uf_df
            .groupby(uf_column)["doses"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        st.bar_chart(
            uf_df
        )

    else:
        st.info(
            "Dados insuficientes para este gráfico."
        )


with col2:
    st.subheader("Doses por vacina")

    if vaccine_column and dose_column:
        vaccine_df = filtered_df.copy()
        vaccine_df["doses"] = convert_to_numeric(vaccine_df[dose_column])

        vaccine_df = (
            vaccine_df
            .groupby(vaccine_column)["doses"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(15)
        )

        st.bar_chart(
            vaccine_df
        )

    else:
        st.info(
            "Dados insuficientes para este gráfico."
        )

st.divider()


# ============================================================
# BASE DE DADOS
# ============================================================

st.subheader("Base de dados")

st.caption(
    f"{len(filtered_df):,} registros encontrados após "
    "a aplicação dos filtros.".replace(",", ".")
)


with st.expander("Visualizar dados"):
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )

st.divider()


# ============================================================
# FONTE
# ============================================================

st.markdown(
    """
    **Fonte dos dados:**  
    [API de Dados Abertos — Saúde Gov.br](https://apidadosabertos.saude.gov.br/v1/#/Vacina%C3%A7%C3%A3o/get_vacinacao_doses_aplicadas_pni_2024)
    """
)


# ============================================================
# NOTÍCIAS - WEB-SCRAPING
# ============================================================

if df_news is not None:
    for _, noticia in df_news.iterrows():
        st.markdown(f"### {noticia['title']}")
        st.write(noticia["text"])