import pandas as pd
import streamlit as st

from src.data_loader import load_data
from src.utils import find_column

# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

df = load_data()

if df.empty:
    st.warning("Não existem dados disponíveis.")
    st.stop()


# ============================================================
# IDENTIFICAÇÃO DAS COLUNAS
# ============================================================

date_column = find_column(df, ["data_vacina"])

uf_column = find_column(df, ["sigla_uf_estabelecimento", "sigla_uf_paciente"])

municipio_column = find_column(
    df, ["nome_municipio_estabelecimento", "nome_municipio_paciente"]
)


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

if date_column:
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")


# ============================================================
# TÍTULO
# ============================================================

st.title("Base de Dados")

st.write(
    """
    Consulte, filtre e exporte os registros de vacinação.
    Utilize os filtros laterais para selecionar os dados
    que deseja visualizar ou baixar.
    """
)

st.divider()


# ============================================================
# SESSION STATE — FILTROS
# ============================================================

if "filtros_dados" not in st.session_state:
    st.session_state.filtros_dados = {"periodo": None, "ufs": [], "municipios": []}


# ============================================================
# SIDEBAR — FILTROS
# ============================================================

st.sidebar.header("Filtros")

with st.sidebar.form("filtros_dados_form"):
    # Período
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
                key="dados_periodo",
            )
        else:
            periodo = None
    else:
        periodo = None

    # Estado / UF
    if uf_column:
        uf_options = sorted(df[uf_column].dropna().astype(str).unique())

        ufs = st.multiselect("Estado (UF)", options=uf_options, key="dados_ufs")
    else:
        ufs = []

    # Cidade / Município
    if municipio_column:
        municipio_options = sorted(df[municipio_column].dropna().astype(str).unique())

        municipios = st.multiselect(
            "Cidade", options=municipio_options, key="dados_municipios"
        )
    else:
        municipios = []

    aplicar = st.form_submit_button("Aplicar filtros", width="stretch")


# ============================================================
# ATUALIZAÇÃO DOS FILTROS
# ============================================================

if aplicar:
    periodo_valido = (
        periodo if isinstance(periodo, tuple) and len(periodo) == 2 else None
    )

    st.session_state.filtros_dados = {
        "periodo": periodo_valido,
        "ufs": ufs,
        "municipios": municipios,
    }


# ============================================================
# LIMPAR FILTROS
# ============================================================


def clear_filters():
    st.session_state.filtros_dados = {"periodo": None, "ufs": [], "municipios": []}

    for key in ["dados_periodo", "dados_ufs", "dados_municipios"]:
        st.session_state.pop(key, None)


st.sidebar.button("Limpar filtros", width="stretch", on_click=clear_filters)


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

filtros = st.session_state.filtros_dados

filtered_df = df.copy()

# Período
if date_column and filtros["periodo"] and len(filtros["periodo"]) == 2:
    start_date, end_date = filtros["periodo"]

    filtered_df = filtered_df[
        (filtered_df[date_column].dt.date >= start_date)
        & (filtered_df[date_column].dt.date <= end_date)
    ]

# Estado / UF
if uf_column and filtros["ufs"]:
    filtered_df = filtered_df[filtered_df[uf_column].astype(str).isin(filtros["ufs"])]

# Cidade / Município
if municipio_column and filtros["municipios"]:
    filtered_df = filtered_df[
        filtered_df[municipio_column].astype(str).isin(filtros["municipios"])
    ]


# ============================================================
# RESUMO DOS FILTROS
# ============================================================

st.sidebar.divider()
st.sidebar.subheader("Filtros aplicados")

if filtros["periodo"]:
    start_date, end_date = filtros["periodo"]

    st.sidebar.caption(f"Período: {start_date:%d/%m/%Y} até {end_date:%d/%m/%Y}")

if filtros["ufs"]:
    st.sidebar.caption(f"Estados: {', '.join(filtros['ufs'])}")

if filtros["municipios"]:
    st.sidebar.caption(f"Cidades selecionadas: {len(filtros['municipios'])}")

if not any([filtros["periodo"], filtros["ufs"], filtros["municipios"]]):
    st.sidebar.caption("Nenhum filtro aplicado.")


# ============================================================
# VISUALIZAÇÃO DA BASE
# ============================================================

st.subheader("Registros de vacinação")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total de registros", f"{len(filtered_df):,}".replace(",", "."))

with col2:
    st.metric("Colunas", len(filtered_df.columns))

if filtered_df.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
else:
    st.dataframe(filtered_df, width="stretch", height=500)


# ============================================================
# DOWNLOAD DOS DADOS FILTRADOS E UPLOAD DE ARQUIVOS
# ============================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Download dos dados")

    st.write("Exporte os registros considerando os filtros aplicados.")

    csv = filtered_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="dados_vacinacao_filtrados.csv",
        mime="text/csv",
        disabled=filtered_df.empty,
    )


with col2:
    st.subheader("Upload de arquivos")
    uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
        st.write("Pré-visualização do arquivo:")
        st.caption(f"{len(uploaded_df):,} registros encontrados.".replace(",", "."))
        st.dataframe(uploaded_df, width="stretch")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
