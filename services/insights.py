def gerar_insights(dados: dict, metricas: dict, ano: int, mes: int) -> list:
    """
    Gera insights priorizados e mais inteligentes.
    """

    insights = []

    df = dados["base_fat"]

    df_mes = df[
        (df["ano"] == ano) &
        (df["mes"] == mes)
    ]

    # =========================
    # META (PRIORIDADE ALTA)
    # =========================
    if metricas["perc_meta"] < 0.8:
        insights.append(("erro", 1, "Desempenho muito abaixo da meta. Necessária ação imediata."))

    elif metricas["perc_meta"] < 1:
        insights.append(("alerta", 2, "Meta ainda não atingida. Ajustes podem garantir o resultado."))

    else:
        insights.append(("sucesso", 3, "Meta atingida. Excelente desempenho."))

    # =========================
    # PROJEÇÃO (ALTA PRIORIDADE)
    # =========================
    if metricas["proj_fat"] < metricas["meta"]:
        insights.append(("erro", 1, "Projeção indica que a meta não será atingida."))

    # =========================
    # TICKET
    # =========================
    if metricas["ticket_medio"] < metricas["ticket_necessario"]:
        insights.append(("alerta", 2, "Ticket médio abaixo do necessário."))

    # =========================
    # QUEDA RECENTE
    # =========================
    ultimos_dias = (
        df_mes
        .groupby(df_mes["data"].dt.day)["faturamento"]
        .sum()
        .tail(5)
    )

    if len(ultimos_dias) >= 2:
        if ultimos_dias.iloc[-1] < ultimos_dias.mean():
            insights.append(("alerta", 3, "Queda recente no faturamento."))

    # =========================
    # OPORTUNIDADE
    # =========================
    if metricas["media_cupons"] > 50:
        insights.append(("sucesso", 4, "Alto fluxo de clientes — oportunidade de aumentar ticket."))

    # =========================
    # ORDENAR POR PRIORIDADE
    # =========================
    insights = sorted(insights, key=lambda x: x[1])

    # =========================
    # LIMITAR (TOP 3)
    # =========================
    insights = insights[:3]

    return insights