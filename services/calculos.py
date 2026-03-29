import pandas as pd
from datetime import datetime
import calendar


def calcular_metricas(dados: dict, ano: int, mes: int) -> dict:
    """
    Calcula métricas principais e projeções para o dashboard.
    """

    df = dados["base_fat"].copy()

    # =========================
    # FILTRO BASE
    # =========================
    df_mes = df[
        (df["ano"] == ano) &
        (df["mes"] == mes)
    ]

    # Segurança
    if df_mes.empty:
        return {
            "total_fat": 0,
            "meta": 0,
            "perc_meta": 0,
            "ticket_medio": 0,
            "media_cupons": 0,
            "proj_fat": 0,
            "fat_dia_necessario": 0,
            "ticket_necessario": 0,
            "dias_restantes": 0
        }

    # =========================
    # MÉTRICAS BASE
    # =========================
    total_fat = df_mes["faturamento"].sum()

    meta = df_mes["meta"].sum(min_count=1)
    meta = 0 if pd.isna(meta) else float(meta)

    total_cupons = df_mes["cupom"].sum()

    ticket_medio = total_fat / total_cupons if total_cupons != 0 else 0

    perc_meta = (total_fat / meta) if meta != 0 else 0

    media_cupons = df_mes["cupom"].mean()

    # =========================
    # MÉTRICAS AUXILIARES
    # =========================
    media_fat_dia = (
        df_mes
        .groupby(df_mes["data"].dt.day)["faturamento"]
        .sum()
        .mean()
    )

    # =========================
    # PROJEÇÕES
    # =========================
    hoje = datetime.today()

    if ano == hoje.year and mes == hoje.month:
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        dias_restantes = ultimo_dia - hoje.day
    else:
        dias_restantes = 0

    dias_restantes = max(dias_restantes, 0)

    proj_fat = total_fat + (media_fat_dia * dias_restantes)

    falta_meta = meta - total_fat

    fat_dia_necessario = (
        falta_meta / dias_restantes
        if dias_restantes > 0 else 0
    )

    ticket_necessario = (
        fat_dia_necessario / media_cupons
        if media_cupons > 0 else 0
    )

    # =========================
    # RETURN FINAL
    # =========================
    return {
        "total_fat": float(total_fat),
        "meta": float(meta),
        "perc_meta": float(perc_meta),
        "ticket_medio": float(ticket_medio),
        "media_cupons": float(media_cupons),
        "proj_fat": float(proj_fat),
        "fat_dia_necessario": float(fat_dia_necessario),
        "ticket_necessario": float(ticket_necessario),
        "dias_restantes": int(dias_restantes),
    }