import pandas as pd


def calcular_metricas(dados: dict, ano: int, mes: int) -> dict:
    """
    Calcula métricas principais para o dashboard.
    """

    df = dados["base_fat"]

    # =========================
    # FILTRO
    # =========================
    df_filtrado = df[
        (df["ano"] == ano) &
        (df["mes"] == mes)
    ]

    # =========================
    # MÉTRICAS
    # =========================
    total_fat = df_filtrado["faturamento"].sum()

    meta = df_filtrado["meta"].sum(min_count=1)
    meta = 0 if pd.isna(meta) else float(meta)

    perc_meta = (total_fat / meta) if meta != 0 else 0

    ticket_medio = (
        df_filtrado["faturamento"].sum() /
        df_filtrado["cupom"].sum()
        if df_filtrado["cupom"].sum() != 0 else 0
    )

    return {
        "total_fat": float(total_fat),
        "meta": float(meta),
        "perc_meta": float(perc_meta),
        "ticket_medio": float(ticket_medio),
    }