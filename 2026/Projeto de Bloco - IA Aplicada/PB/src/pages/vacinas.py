import pandas as pd
import streamlit as st

from src.data_loader import load_data
from src.utils import find_column

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================


def clear_filters():
    """Limpa os filtros e seus respectivos estados."""

    st.session_state.filtros_vacinas = {
        "periodo": None,
        "ufs": [],
        "municipios": [],
        "vacinas": [],
    }

    for key in ["filtro_periodo", "filtro_ufs", "filtro_municipios", "filtro_vacinas"]:
        st.session_state.pop(key, None)


def apply_filters(df, columns, filters):
    """Aplica os filtros selecionados à base de vacinação."""

    filtered_df = df.copy()

    date_column = columns["date"]
    uf_column = columns["uf"]
    municipio_column = columns["municipio"]
    vaccine_column = columns["vaccine"]

    # Filtro por período
    periodo = filters["periodo"]

    if date_column and periodo and len(periodo) == 2:
        start_date, end_date = periodo

        filtered_df = filtered_df[
            (filtered_df[date_column].dt.date >= start_date)
            & (filtered_df[date_column].dt.date <= end_date)
        ]

    # Filtro por UF
    if uf_column and filters["ufs"]:
        filtered_df = filtered_df[
            filtered_df[uf_column].astype(str).isin(filters["ufs"])
        ]

    # Filtro por município
    if municipio_column and filters["municipios"]:
        filtered_df = filtered_df[
            filtered_df[municipio_column].astype(str).isin(filters["municipios"])
        ]

    # Filtro por vacina
    if vaccine_column and filters["vacinas"]:
        filtered_df = filtered_df[
            filtered_df[vaccine_column].astype(str).isin(filters["vacinas"])
        ]

    return filtered_df


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

df = load_data()

if df.empty:
    st.warning("Não existem dados de vacinação disponíveis.")
    st.stop()


# ============================================================
# IDENTIFICAÇÃO DAS COLUNAS
# ============================================================

columns = {
    "date": find_column(df, ["data_vacina"]),
    "uf": find_column(df, ["sigla_uf_estabelecimento", "sigla_uf_paciente"]),
    "municipio": find_column(
        df, ["nome_municipio_estabelecimento", "nome_municipio_paciente"]
    ),
    "vaccine": find_column(df, ["descricao_vacina_fabricante"]),
}

date_column = columns["date"]
uf_column = columns["uf"]
municipio_column = columns["municipio"]
vaccine_column = columns["vaccine"]


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

if date_column:
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")


# ============================================================
# TÍTULO
# ============================================================

st.title("Análise de Vacinação")

st.write(
    """
    Explore os dados de vacinação no Brasil por período,
    localização e fabricante da vacina.
    """
)

st.divider()


# ============================================================
# SESSION STATE — FILTROS
# ============================================================

if "filtros_vacinas" not in st.session_state:
    st.session_state.filtros_vacinas = {
        "periodo": None,
        "ufs": [],
        "municipios": [],
        "vacinas": [],
    }


# ============================================================
# SIDEBAR — FILTROS
# ============================================================

st.sidebar.header("Filtros")

st.sidebar.write("Selecione os filtros e clique em Aplicar filtros.")

# Opções de período
if date_column:
    valid_dates = df[date_column].dropna()

    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
    else:
        min_date = None
        max_date = None
else:
    min_date = None
    max_date = None


with st.sidebar.form("filtros_vacinas_form"):
    # Período
    if min_date and max_date:
        periodo = st.date_input(
            "Período",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="filtro_periodo",
        )
    else:
        periodo = None

    # UF
    if uf_column:
        uf_options = sorted(df[uf_column].dropna().astype(str).unique())

        ufs = st.multiselect("UF", options=uf_options, key="filtro_ufs")
    else:
        ufs = []

    # Município
    if municipio_column:
        municipio_options = sorted(df[municipio_column].dropna().astype(str).unique())

        municipios = st.multiselect(
            "Município", options=municipio_options, key="filtro_municipios"
        )
    else:
        municipios = []

    # Vacina
    if vaccine_column:
        vaccine_options = sorted(df[vaccine_column].dropna().astype(str).unique())

        vacinas = st.multiselect(
            "Vacina", options=vaccine_options, key="filtro_vacinas"
        )
    else:
        vacinas = []

    aplicar = st.form_submit_button("Aplicar filtros", width="stretch")


# Atualiza os filtros aplicados
if aplicar:
    periodo_valido = (
        periodo if isinstance(periodo, tuple) and len(periodo) == 2 else None
    )

    st.session_state.filtros_vacinas = {
        "periodo": periodo_valido,
        "ufs": ufs,
        "municipios": municipios,
        "vacinas": vacinas,
    }


# Botão para limpar os filtros
st.sidebar.button("Limpar filtros", width="stretch", on_click=clear_filters)


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

filtros = st.session_state.filtros_vacinas

filtered_df = apply_filters(df, columns, filtros)


# ============================================================
# FILTROS APLICADOS
# ============================================================

st.sidebar.divider()
st.sidebar.subheader("Filtros aplicados")

if filtros["periodo"]:
    start_date, end_date = filtros["periodo"]

    st.sidebar.caption(f"Período: {start_date:%d/%m/%Y} até {end_date:%d/%m/%Y}")

if filtros["ufs"]:
    st.sidebar.caption(f"UF: {', '.join(filtros['ufs'])}")

if filtros["municipios"]:
    st.sidebar.caption(f"Municípios: {len(filtros['municipios'])}")

if filtros["vacinas"]:
    st.sidebar.caption(f"Vacinas: {len(filtros['vacinas'])}")

if not any(
    [filtros["periodo"], filtros["ufs"], filtros["municipios"], filtros["vacinas"]]
):
    st.sidebar.caption("Nenhum filtro aplicado.")


# ============================================================
# VALIDAÇÃO DOS RESULTADOS
# ============================================================

if filtered_df.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()


# ============================================================
# INDICADORES
# ============================================================

st.subheader("Indicadores")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Doses aplicadas", f"{len(filtered_df):,}".replace(",", "."))

with col2:
    st.metric("UFs", filtered_df[uf_column].nunique() if uf_column else 0)

with col3:
    st.metric(
        "Municípios", filtered_df[municipio_column].nunique() if municipio_column else 0
    )

with col4:
    st.metric("Vacinas", filtered_df[vaccine_column].nunique() if vaccine_column else 0)

st.divider()


# ============================================================
# GRÁFICO — EVOLUÇÃO TEMPORAL
# ============================================================

st.subheader("Evolução da vacinação")

if date_column:
    temporal_df = (
        filtered_df.dropna(subset=[date_column])
        .groupby(date_column)
        .size()
        .sort_index()
    )

    temporal_df.name = "Doses aplicadas"

    st.line_chart(temporal_df)

else:
    st.info("Não foi possível construir o gráfico temporal.")


# ============================================================
# GRÁFICOS — UF E VACINA
# ============================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Doses por UF")

    if uf_column:
        uf_df = filtered_df.groupby(uf_column).size().sort_values(ascending=False)

        uf_df.name = "Doses aplicadas"

        st.bar_chart(uf_df)

    else:
        st.info("Dados insuficientes para este gráfico.")


with col2:
    st.subheader("Doses por vacina")

    if vaccine_column:
        vaccine_df = (
            filtered_df.groupby(vaccine_column)
            .size()
            .sort_values(ascending=False)
            .head(15)
        )

        vaccine_df.name = "Doses aplicadas"

        st.bar_chart(vaccine_df)

    else:
        st.info("Dados insuficientes para este gráfico.")


st.divider()
