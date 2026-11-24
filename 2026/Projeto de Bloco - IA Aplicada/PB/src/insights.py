"""Transforma a base de vacinação em texto de indicadores para o prompt da LLM."""

import pandas as pd

from src.utils import find_column

TOP_N = 5


def _pct(parte: int, total: int) -> str:
    return f"{parte / total * 100:.1f}%" if total else "0,0%"


def build_data_context(df: pd.DataFrame, filtros_descricao: str = "") -> str:
    """Gera um texto com indicadores agregados da base (já filtrada) para alimentar a LLM.

    Só entram números calculados aqui; a LLM é instruída a citar apenas estes valores.
    """
    total = len(df)
    if total == 0:
        return "Nenhum registro para os filtros selecionados."

    uf_col = find_column(df, ["sigla_uf_estabelecimento", "sigla_uf_paciente"])
    mun_col = find_column(df, ["nome_municipio_estabelecimento", "nome_municipio_paciente"])
    fab_col = find_column(df, ["descricao_vacina_fabricante"])
    date_col = find_column(df, ["data_vacina"])

    linhas = [f"- Filtros aplicados: {filtros_descricao or 'nenhum (base completa)'}"]
    linhas.append(f"- Total de doses aplicadas (registros): {total:,}".replace(",", "."))

    if date_col:
        datas = pd.to_datetime(df[date_col], errors="coerce", utc=True).dropna()
        if not datas.empty:
            linhas.append(f"- Período dos registros: {datas.min():%d/%m/%Y} a {datas.max():%d/%m/%Y}")
            por_mes = datas.dt.strftime("%m/%Y").value_counts().sort_index()
            linhas.append(
                "- Doses por mês: " + "; ".join(f"{m}: {n:,}".replace(",", ".") for m, n in por_mes.items())
            )

    if uf_col:
        contagem = df[uf_col].value_counts()
        linhas.append(f"- UFs com registros: {contagem.size}")
        top = "; ".join(f"{uf}: {n:,} ({_pct(n, total)})".replace(",", ".") for uf, n in contagem.head(TOP_N).items())
        linhas.append(f"- Top {min(TOP_N, contagem.size)} UFs por doses: {top}")

    if mun_col:
        linhas.append(f"- Municípios com registros: {df[mun_col].nunique()}")

    if fab_col:
        contagem = df[fab_col].value_counts()
        top = "; ".join(f"{f}: {n:,} ({_pct(n, total)})".replace(",", ".") for f, n in contagem.head(TOP_N).items())
        linhas.append(f"- Top {min(TOP_N, contagem.size)} fabricantes por doses: {top}")

    if "tipo_sexo_paciente" in df.columns:
        sexo = df["tipo_sexo_paciente"].value_counts()
        linhas.append("- Sexo: " + "; ".join(f"{s}: {_pct(n, total)}" for s, n in sexo.items()))

    if "numero_idade_paciente" in df.columns:
        idade = pd.to_numeric(df["numero_idade_paciente"], errors="coerce").dropna()
        if not idade.empty:
            linhas.append(
                f"- Idade: mediana {idade.median():.0f} anos; média {idade.mean():.1f}; "
                f"{_pct(int((idade < 12).sum()), len(idade))} dos registros são de menores de 12 anos; "
                f"{_pct(int((idade >= 60).sum()), len(idade))} de pessoas com 60 anos ou mais"
            )

    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Destaques determinísticos (sem LLM): todos os números do resumo vêm daqui
# ---------------------------------------------------------------------------


def _n(valor: int) -> str:
    """Inteiro com separador de milhar brasileiro."""
    return f"{valor:,}".replace(",", ".")


def _p(parte: int, total: int) -> str:
    """Percentual com vírgula decimal."""
    return f"{parte / total * 100:.1f}%".replace(".", ",") if total else "0,0%"


def build_highlights(df: pd.DataFrame, filtros_descricao: str = "") -> str:
    """Resumo executivo montado por template: Panorama, Destaques e Pontos de atenção.

    Nenhum texto aqui é gerado por IA, então todo número e rótulo é exato.
    """
    total = len(df)
    if total == 0:
        return "Nenhum registro para os filtros selecionados."

    uf_col = find_column(df, ["sigla_uf_estabelecimento", "sigla_uf_paciente"])
    mun_col = find_column(df, ["nome_municipio_estabelecimento", "nome_municipio_paciente"])
    fab_col = find_column(df, ["descricao_vacina_fabricante"])
    date_col = find_column(df, ["data_vacina"])

    panorama = [f"{_n(total)} doses aplicadas (registros)"]
    atencao = [
        "Os registros não trazem a população-alvo, então não é possível calcular cobertura vacinal; "
        "os números descrevem volume de doses registradas."
    ]
    destaques: list[str] = []

    if date_col:
        datas = pd.to_datetime(df[date_col], errors="coerce", utc=True).dropna()
        if not datas.empty:
            panorama.append(f"entre {datas.min():%d/%m/%Y} e {datas.max():%d/%m/%Y}")
            meses = datas.dt.tz_localize(None).dt.to_period("M").value_counts().sort_index()
            todos = pd.period_range(meses.index.min(), meses.index.max(), freq="M")
            meses = meses.reindex(todos, fill_value=0)
            pico = meses.idxmax()
            destaques.append(f"Mês com mais doses: {pico.strftime('%m/%Y')} ({_n(int(meses.max()))}, {_p(int(meses.max()), total)} do total).")
            fracos = [f"{m.strftime('%m/%Y')} ({_n(int(n))})" for m, n in meses.items() if n / total < 0.01]
            if fracos:
                atencao.append("Meses com menos de 1% dos registros: " + ", ".join(fracos) + ". A série temporal é irregular.")

    if uf_col:
        ufs = df[uf_col].value_counts()
        panorama.append(f"em {ufs.size} UF(s)")
        if ufs.size > 1:
            top = "; ".join(f"{u} {_n(int(n))} ({_p(int(n), total)})" for u, n in ufs.head(3).items())
            destaques.append(f"UFs com mais doses: {top}.")
        elif mun_col:
            muns = df[mun_col].value_counts()
            top = "; ".join(f"{m} {_n(int(n))} ({_p(int(n), total)})" for m, n in muns.head(3).items())
            destaques.append(f"Municípios de {ufs.index[0]} com mais doses: {top}.")

    if fab_col:
        fabs = df[fab_col].value_counts()
        top = "; ".join(f"{f} {_n(int(n))} ({_p(int(n), total)})" for f, n in fabs.head(3).items())
        destaques.append(f"Fabricantes com mais doses registradas: {top}.")

    if "numero_idade_paciente" in df.columns:
        idade = pd.to_numeric(df["numero_idade_paciente"], errors="coerce").dropna()
        if not idade.empty:
            destaques.append(
                f"Faixa etária: mediana de {idade.median():.0f} anos; "
                f"{_p(int((idade < 12).sum()), len(idade))} dos registros são de menores de 12 anos e "
                f"{_p(int((idade >= 60).sum()), len(idade))} de pessoas com 60 anos ou mais."
            )

    linhas = []
    if filtros_descricao:
        linhas.append(f"*Filtros: {filtros_descricao}*\n")
    linhas.append("**Panorama:** " + ", ".join(panorama) + ".\n")
    linhas.append("**Destaques:**")
    linhas += [f"- {d}" for d in destaques]
    linhas.append("\n**Pontos de atenção:**")
    linhas += [f"- {a}" for a in atencao]
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Séries para os gráficos do dashboard (mesmos números que alimentam a IA)
# ---------------------------------------------------------------------------


def monthly_counts(df: pd.DataFrame) -> pd.Series:
    """Doses por mês (inclui meses sem registro), índice no formato 'AAAA-MM'."""
    date_col = find_column(df, ["data_vacina"])
    if not date_col:
        return pd.Series(dtype=int)
    datas = pd.to_datetime(df[date_col], errors="coerce", utc=True).dropna()
    if datas.empty:
        return pd.Series(dtype=int)
    meses = datas.dt.tz_localize(None).dt.to_period("M").value_counts().sort_index()
    meses = meses.reindex(pd.period_range(meses.index.min(), meses.index.max(), freq="M"), fill_value=0)
    meses.index = meses.index.strftime("%Y-%m")
    return meses


def top_counts(df: pd.DataFrame, candidates: list[str], n: int = 10) -> pd.Series:
    """Top-n valores mais frequentes da primeira coluna existente em ``candidates``."""
    col = find_column(df, candidates)
    return df[col].value_counts().head(n) if col else pd.Series(dtype=int)


def age_bands(df: pd.DataFrame) -> pd.Series:
    """Doses por faixa etária."""
    if "numero_idade_paciente" not in df.columns:
        return pd.Series(dtype=int)
    idade = pd.to_numeric(df["numero_idade_paciente"], errors="coerce").dropna()
    faixas = pd.cut(
        idade,
        bins=[-1, 4, 11, 17, 29, 59, 200],
        labels=["0-4", "5-11", "12-17", "18-29", "30-59", "60+"],
    )
    return faixas.value_counts().sort_index()
