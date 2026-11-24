"""Dashboard do ciclo completo de Ciência de Dados: coleta → preparação → IA → insights → interação."""

import altair as alt
import pandas as pd
import streamlit as st

from src.data_loader import load_data, load_news
from src.insights import (
    age_bands,
    build_data_context,
    build_highlights,
    monthly_counts,
    top_counts,
)
from src.llm_client import LLMError, perguntar_dados, resumir_dados, resumir_noticia, status_ia

TODAS = "Todas"


@st.cache_data
def load_base() -> pd.DataFrame:
    """Base processada com a coluna auxiliar 'mes' (AAAA-MM) para filtrar por mês."""
    df = load_data().copy()
    datas = pd.to_datetime(df["data_vacina"], errors="coerce", utc=True)
    df["mes"] = datas.dt.tz_localize(None).dt.strftime("%Y-%m")
    return df


def barras_horizontais(serie: pd.Series) -> None:
    """Barras horizontais ordenadas por valor, com eixo iniciando em zero e tooltip."""
    dados = serie.rename_axis("item").reset_index(name="doses")
    grafico = (
        alt.Chart(dados)
        .mark_bar()
        .encode(
            x=alt.X("doses:Q", title="Doses"),
            y=alt.Y("item:N", sort="-x", title=None),
            tooltip=["item", "doses"],
        )
    )
    st.altair_chart(grafico, width="stretch")


def barras_verticais(serie: pd.Series, titulo_x: str) -> None:
    """Barras verticais na ordem do índice, com eixo y iniciando em zero."""
    dados = serie.rename_axis("categoria").reset_index(name="doses")
    dados["categoria"] = dados["categoria"].astype(str)
    grafico = (
        alt.Chart(dados)
        .mark_bar()
        .encode(
            x=alt.X("categoria:N", sort=None, title=titulo_x, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("doses:Q", title="Doses", scale=alt.Scale(domainMin=0)),
            tooltip=["categoria", "doses"],
        )
    )
    st.altair_chart(grafico, width="stretch")


def recorte_descricao(uf: str, mes: str) -> str:
    partes = []
    if uf != TODAS:
        partes.append(f"UF={uf}")
    if mes != TODAS:
        partes.append(f"mês={mes}")
    return "; ".join(partes)


# ============================================================
# CABEÇALHO E STATUS DA IA
# ============================================================

st.title("Ciclo de Dados e IA")
st.write(
    "Da coleta dos dados públicos ao insight gerado por IA: acompanhe cada etapa, "
    "veja os resultados em gráficos e converse com o modelo sobre o recorte escolhido."
)

ia = status_ia()
if not ia["online"]:
    st.sidebar.error("API de IA offline. Inicie com: `uvicorn api.main:app`")
elif not ia["pronto"]:
    st.sidebar.warning("API online, mas o modelo de linguagem não está carregado.")
else:
    st.sidebar.success(f"IA online: {ia['modelo']}")

st.graphviz_chart(
    """
    digraph G {
        rankdir=LR; bgcolor="transparent";
        node [shape=box, style="rounded,filled", fillcolor="#e8f1fb", color="#4b7bb5", fontname="Helvetica", fontsize=11];
        edge [color="#4b7bb5"];
        A [label="1. Coleta\\nAPI Gov.br + scraping"];
        B [label="2. Preparação\\nlimpeza e padronização"];
        C [label="3. Análise\\nindicadores e gráficos"];
        D [label="4. IA (LLM local)\\ninterpretação e respostas"];
        E [label="5. Insight\\ngestor do SUS"];
        A -> B -> C -> D -> E;
    }
    """,
    width="stretch",
)

with st.spinner("Carregando dados..."):
    base = load_base()
    noticias = load_news()

# ============================================================
# RECORTE (afeta as etapas 3 e 4)
# ============================================================

col_uf, col_mes, col_info = st.columns([1, 1, 2])
with col_uf:
    uf_sel = st.selectbox("UF do recorte", [TODAS] + sorted(base["sigla_uf_estabelecimento"].unique()))
with col_mes:
    meses_validos = sorted(m for m in base["mes"].dropna().unique())
    mes_sel = st.selectbox("Mês do recorte", [TODAS] + meses_validos)

recorte = base
if uf_sel != TODAS:
    recorte = recorte[recorte["sigla_uf_estabelecimento"] == uf_sel]
if mes_sel != TODAS:
    recorte = recorte[recorte["mes"] == mes_sel]

with col_info:
    st.metric("Doses no recorte", f"{len(recorte):,}".replace(",", "."))

if recorte.empty:
    st.warning("Nenhum registro para o recorte escolhido. Ajuste a UF ou o mês.")
    st.stop()

filtros_txt = recorte_descricao(uf_sel, mes_sel)
destaques = build_highlights(recorte, filtros_txt)

tab1, tab2, tab3, tab4 = st.tabs(
    ["1 · Coleta", "2 · Preparação", "3 · IA aplicada aos dados", "4 · Pergunte à IA"]
)

# ============================================================
# 1 · COLETA
# ============================================================

with tab1:
    st.subheader("Dados coletados")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Registros", f"{len(base):,}".replace(",", "."))
    c2.metric("Colunas", base.shape[1] - 1)
    c3.metric("UFs", base["sigla_uf_estabelecimento"].nunique())
    c4.metric("Municípios", base["nome_municipio_estabelecimento"].nunique())
    c5.metric("Notícias", len(noticias))

    st.markdown(
        """
| Fonte | Tipo | Método | Uso no projeto |
|---|---|---|---|
| Dados Abertos Saúde (Gov.br), doses aplicadas PNI | Estruturada | API REST paginada (`requests`) | Indicadores, gráficos, API, resumo e perguntas à IA |
| Blog Medicalway | Texto não estruturado | Web scraping (`requests` + `BeautifulSoup`) | Página de notícias e resumos por IA |
"""
    )

    st.markdown("**Amostra da base processada**")
    st.dataframe(base.drop(columns=["mes"]).head(10), width="stretch")

    st.markdown("**Notícias coletadas por scraping**")
    tabela_noticias = pd.DataFrame(
        {
            "Título": noticias["title"],
            "Caracteres do texto": noticias["text"].str.len(),
            "URL": noticias["url"],
        }
    )
    st.dataframe(
        tabela_noticias,
        width="stretch",
        hide_index=True,
        column_config={"URL": st.column_config.LinkColumn("URL")},
    )

# ============================================================
# 2 · PREPARAÇÃO
# ============================================================

with tab2:
    st.subheader("Preparação e qualidade")
    st.markdown(
        """
Etapas aplicadas em `src/preprocessing.py`:
1. Remoção de colunas técnicas e de dados pessoais (LGPD).
2. Preenchimento de ausentes (país, etnia, UF/município do paciente; moda ou "Não informado").
3. Remoção de duplicatas e de idades fora de 0–110 anos.
4. Padronização de textos e unificação de fabricantes.
"""
    )

    nulos = int(base.drop(columns=["mes"]).isna().sum().sum())
    dups = int(base.drop(columns=["mes"]).duplicated().sum())
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Células nulas (agora)", nulos)
    q2.metric("Linhas duplicadas (agora)", dups)
    q3.metric("Idade máxima", int(base["numero_idade_paciente"].max()))
    q4.metric("Meses com registros", base["mes"].nunique())

    st.caption(
        f"Período dos registros: {base['mes'].min()} a {base['mes'].max()}. "
        "Antes da preparação (medido em 23/11/2026, ver docs/tdsp/04): 225.958 linhas, 2.330 duplicatas, "
        "95,7% das células preenchidas. Depois: 223.625 linhas e 100% preenchidas."
    )

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Doses por mês (base completa)**")
        barras_verticais(monthly_counts(base), "Mês")
        st.caption(
            "Lacuna conhecida: meses com poucos ou nenhum registro (ex.: março). "
            "A série temporal é irregular."
        )
    with g2:
        st.markdown("**Doses por faixa etária (base completa)**")
        barras_verticais(age_bands(base), "Faixa etária (anos)")

# ============================================================
# 3 · IA APLICADA
# ============================================================

with tab3:
    st.subheader(f"Resultados para o recorte: {filtros_txt or 'Brasil, todo o período'}")

    # Insights determinísticos (números exatos, sem IA)
    total = len(recorte)
    meses_rec = monthly_counts(recorte)
    top_uf = top_counts(recorte, ["sigla_uf_estabelecimento"], 1)
    idade = pd.to_numeric(recorte["numero_idade_paciente"], errors="coerce").dropna()
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Mês de pico", meses_rec.idxmax() if not meses_rec.empty else "-")
    i2.metric(
        "UF líder" if uf_sel == TODAS else "UF",
        top_uf.index[0] if not top_uf.empty else "-",
        f"{top_uf.iloc[0] / total * 100:.1f}% das doses".replace(".", ",") if not top_uf.empty else None,
        delta_color="off",
    )
    i3.metric("Menores de 12 anos", f"{(idade < 12).mean() * 100:.1f}%".replace(".", ","))
    i4.metric("60 anos ou mais", f"{(idade >= 60).mean() * 100:.1f}%".replace(".", ","))

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Doses por mês**")
        barras_verticais(meses_rec, "Mês")
        st.markdown("**Fabricantes com mais doses**")
        barras_horizontais(top_counts(recorte, ["descricao_vacina_fabricante"], 8))
    with g2:
        if uf_sel == TODAS:
            st.markdown("**UFs com mais doses**")
            barras_horizontais(top_counts(recorte, ["sigla_uf_estabelecimento"], 10))
        else:
            st.markdown(f"**Municípios de {uf_sel} com mais doses**")
            barras_horizontais(top_counts(recorte, ["nome_municipio_estabelecimento"], 10))
        st.markdown("**Faixa etária**")
        barras_verticais(age_bands(recorte), "Faixa etária (anos)")

    st.divider()
    st.markdown("### Resumo executivo")
    st.caption(
        "Números e rótulos calculados em Python (sem IA). A LLM local escreve apenas o parágrafo de "
        "interpretação, sem citar números."
    )
    st.markdown(destaques)

    chave_resumo = f"ia_resumo|{filtros_txt}"
    if st.button("Gerar interpretação com IA", key="btn_interpretar"):
        with st.spinner("A LLM local está interpretando o recorte (20 a 40 s)..."):
            try:
                st.session_state[chave_resumo] = resumir_dados(destaques, build_data_context(recorte, filtros_txt))
            except LLMError as e:
                st.session_state.pop(chave_resumo, None)
                st.error(str(e))
    resultado = st.session_state.get(chave_resumo)
    if resultado:
        if resultado.get("interpretacao"):
            st.info(f"**Interpretação (IA):** {resultado['interpretacao']}")
        else:
            st.warning("A IA não gerou uma interpretação válida desta vez (a regra 'sem números' foi violada).")
        st.caption(f"{resultado['modelo']} · {resultado['tempo_geracao_segundos']} s")

    st.divider()
    st.markdown("### Resumo de uma notícia (texto não estruturado)")
    titulos = noticias["title"].tolist()
    escolhida = st.selectbox("Notícia", range(len(titulos)), format_func=lambda i: titulos[i])
    chave_noticia = f"ia_noticia|{escolhida}"
    if st.button("Resumir notícia com IA", key="btn_noticia"):
        with st.spinner("A LLM local está resumindo a notícia (60 a 90 s)..."):
            try:
                st.session_state[chave_noticia] = resumir_noticia(titulos[escolhida], noticias["text"].iloc[escolhida])
            except LLMError as e:
                st.session_state.pop(chave_noticia, None)
                st.error(str(e))
    res_not = st.session_state.get(chave_noticia)
    if res_not:
        st.info(res_not["resumo"])
        st.caption(
            f"{res_not['modelo']} · {res_not['tempo_geracao_segundos']} s · "
            f"{res_not.get('blocos_processados', 1)} bloco(s). Resumo automático: confira o texto original."
        )
        st.link_button("Ler notícia original", noticias["url"].iloc[escolhida])

# ============================================================
# 4 · PERGUNTE À IA
# ============================================================

with tab4:
    st.subheader("Pergunte à IA sobre o recorte")
    st.caption(
        "A LLM responde somente com base no resumo numérico do recorte atual (visível abaixo). "
        "Números citados que não estejam no resumo são sinalizados."
    )
    with st.expander("Contexto enviado à IA"):
        st.markdown(destaques)

    if "chat_dados" not in st.session_state:
        st.session_state.chat_dados = []

    sugestoes = [
        "Qual o mês com mais doses?",
        "O que se destaca no perfil etário?",
        "Há lacunas nos dados que eu deva conhecer?",
    ]
    cols = st.columns(len(sugestoes))
    pergunta_pendente = None
    for col, texto in zip(cols, sugestoes):
        if col.button(texto, key=f"sug_{texto}"):
            pergunta_pendente = texto

    if st.button("Limpar conversa", key="limpar_chat"):
        st.session_state.chat_dados = []

    for msg in st.session_state.chat_dados:
        with st.chat_message(msg["papel"]):
            st.write(msg["texto"])
            if msg.get("aviso"):
                st.warning(msg["aviso"])
            if msg.get("meta"):
                st.caption(msg["meta"])

    digitada = st.chat_input("Ex.: Qual UF concentra mais doses neste recorte?")
    pergunta = digitada or pergunta_pendente

    if pergunta:
        st.session_state.chat_dados.append({"papel": "user", "texto": f"{pergunta}  \n*(recorte: {filtros_txt or 'Brasil, todo o período'})*"})
        with st.chat_message("user"):
            st.write(pergunta)
        with st.chat_message("assistant"):
            with st.spinner("A LLM local está respondendo (20 a 40 s)..."):
                try:
                    r = perguntar_dados(pergunta, destaques)
                    aviso = None
                    if r["numeros_nao_verificados"]:
                        aviso = (
                            "Atenção: a resposta cita números que não constam no resumo "
                            f"({', '.join(r['numeros_nao_verificados'])}). Verifique antes de usar."
                        )
                    st.session_state.chat_dados.append(
                        {
                            "papel": "assistant",
                            "texto": r["resposta"],
                            "aviso": aviso,
                            "meta": f"{r['modelo']} · {r['tempo_geracao_segundos']} s",
                        }
                    )
                except LLMError as e:
                    st.session_state.chat_dados.append({"papel": "assistant", "texto": f"Erro: {e}"})
        st.rerun()
