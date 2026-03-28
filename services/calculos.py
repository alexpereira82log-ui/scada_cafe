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
    # Total Faturamento
    total_fat = df_filtrado["faturamento"].sum()

    # Meta atual
    meta = df_filtrado["meta"].sum(min_count=1)
    meta = 0 if pd.isna(meta) else float(meta)

    # Percentual atingido da meta
    perc_meta = (total_fat / meta) if meta != 0 else 0

    # Ticket Médio
    ticket_medio = (
        df_filtrado["faturamento"].sum() /
        df_filtrado["cupom"].sum()
        if df_filtrado["cupom"].sum() != 0 else 0
    )

    # Média de cupons por dia
    df_cupom = dados["base_fat"].copy()

    df_cupom = df_cupom[
        (df_cupom["ano"] == ano) &
        (df_cupom["mes"] == mes)
    ]

    media_cupons = df_cupom["cupom"].mean() if not df_cupom.empty else 0

    # Return da função:
    return {
        "total_fat": float(total_fat),
        "meta": float(meta),
        "perc_meta": float(perc_meta),
        "ticket_medio": float(ticket_medio),
        "media_cupons": int(media_cupons)
    }