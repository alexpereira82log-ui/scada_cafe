import pandas as pd


# ============================================================
# FATURAMENTO POR MÊS
# ============================================================
def faturamento_por_mes(dados: dict, ano: int) -> pd.DataFrame:
    df = dados["base_fat"]

    df_ano = df[df["ano"] == ano]

    resultado = (
        df_ano
        .groupby(["mes", "mes_nome"])[["faturamento", "meta"]]
        .sum()
        .reset_index()
        .sort_values("mes")
    )

    return resultado


# ============================================================
# FATURAMENTO POR DIA
# ============================================================
def faturamento_por_dia(dados: dict, ano: int, mes: int) -> pd.DataFrame:
    df = dados["base_fat"]

    df_mes = df[(df["ano"] == ano) & (df["mes"] == mes)]

    resultado = df_mes[["data", "faturamento"]].dropna()

    return resultado


# ============================================================
# TOP PRODUTOS
# ============================================================
def top_produtos(dados: dict, ano: int) -> pd.DataFrame:
    df = dados["base_produtos"]

    df_ano = df[df["ano"] == ano]

    resultado = (
        df_ano
        .groupby("produto")
        .agg({
            "qtd": "sum",
            "valor_total": "sum"
        })
        .reset_index()
        .sort_values("qtd", ascending=False)
    )

    return resultado


# ============================================================
# PERDAS POR MOTIVO
# ============================================================
def perdas_por_motivo(dados: dict, ano: int, mes: int) -> pd.DataFrame:
    df = dados["base_perdas"]

    df_filtrado = df[
        (df["data"].dt.year == ano) &
        (df["data"].dt.month == mes)
    ]

    resultado = (
        df_filtrado
        .groupby("motivo")[["item"]]
        .count()
        .reset_index()
        .sort_values("item", ascending=False)
    )

    return resultado