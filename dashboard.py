import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.connection import carregar_dados
from utils.tratamento import tratar_dados
from services.analises import faturamento_por_mes, top_produtos
from services.calculos import calcular_metricas


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard Scada Café",
    layout="wide"
)

st.title("📊 Dashboard Scada Café")
st.markdown("---")

# =========================
# CARREGAR DADOS
# =========================
dados = carregar_dados()
dados = tratar_dados(dados)

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")

anos = sorted(dados["base_fat"]["ano"].dropna().unique())
ano = st.sidebar.selectbox("Selecione o Ano", anos)

meses = list(range(1, 13))
mes = st.sidebar.selectbox("Selecione o Mês", meses)

# =========================
# MÉTRICAS (USADA EM TODAS AS ABAS)
# =========================
metricas = calcular_metricas(dados, ano, mes)
atingiu_meta = metricas["perc_meta"] >= 1
cor_meta = "normal" if atingiu_meta else "inverse"

# =========================
# CRIAR ABAS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Geral",
    "📈 Faturamento",
    "🏆 Produtos",
    "⚠️ Perdas"
])

# ======================================================
# 📊 ABA 1 — VISÃO GERAL
# ======================================================
with tab1:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Faturamento", f"R$ {metricas['total_fat']:,.2f}")
    col2.metric("Meta", f"R$ {metricas['meta']:,.2f}")

    col3.metric(
        "% Meta",
        f"{metricas['perc_meta']:.0%}",
        delta="Meta atingida" if atingiu_meta else "Abaixo da meta",
        delta_color=cor_meta
    )

    col4.metric("Ticket Médio", f"R$ {metricas['ticket_medio']:,.2f}")

    # Gauge + comparação
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Atingimento da Meta")

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metricas["perc_meta"] * 100,
            title={'text': "Meta (%)"},
            gauge={
                'axis': {'range': [0, 150]},
                'bar': {'color': "green" if atingiu_meta else "red"},
                'steps': [
                    {'range': [0, 100], 'color': "lightcoral"},
                    {'range': [100, 150], 'color': "lightgreen"},
                ],
            }
        ))

        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.subheader("📊 Comparação Mensal")

        mes_anterior = mes - 1 if mes > 1 else 12
        metricas_ant = calcular_metricas(dados, ano, mes_anterior)

        delta_fat = metricas["total_fat"] - metricas_ant["total_fat"]

        st.metric(
            "Faturamento Atual",
            f"R$ {metricas['total_fat']:,.2f}",
            delta=f"{delta_fat:,.2f}"
        )

    # Insight
    st.markdown("### 🔍 Insight automático")

    if metricas["perc_meta"] >= 1:
        st.success("Meta atingida! Excelente performance.")
    elif metricas["perc_meta"] >= 0.9:
        st.warning("Próximo da meta. Pequeno ajuste pode bater o objetivo.")
    else:
        st.error("Abaixo da meta. Necessário plano de ação")


# ======================================================
# 📈 ABA 2 — FATURAMENTO
# ======================================================
with tab2:

    st.subheader("📈 Evolução do Faturamento")

    df_fat = faturamento_por_mes(dados, ano)

    fig_fat = px.bar(
        df_fat,
        x="mes",
        y="faturamento",
        text="faturamento",
        title="Faturamento Mensal"
    )

    fig_fat.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    # Faturamento diário
    df_dia = dados["base_fat"]
    df_dia = df_dia[
        (df_dia["ano"] == ano) &
        (df_dia["mes"] == mes)
    ]

    df_dia = df_dia.groupby(df_dia["data"].dt.day)["faturamento"].sum().reset_index()

    fig_dia = px.line(
        df_dia,
        x="data",
        y="faturamento",
        markers=True,
        title="Faturamento Diário"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_fat, use_container_width=True)

    with col2:
        st.plotly_chart(fig_dia, use_container_width=True)


# ======================================================
# 🏆 ABA 3 — PRODUTOS
# ======================================================
with tab3:

    st.subheader("🏆 Performance de Produtos")

    df_prod = top_produtos(dados, ano).head(10)

    fig_prod = px.bar(
        df_prod,
        x="qtd",
        y="produto",
        orientation="h",
        text="qtd",
        title="Top Produtos"
    )

    fig_prod.update_layout(yaxis={'categoryorder': 'total ascending'})

    st.plotly_chart(fig_prod, use_container_width=True)


# ======================================================
# ⚠️ ABA 4 — PERDAS
# ======================================================
with tab4:

    st.subheader("⚠️ Análise de Perdas")

    df_perdas = dados["base_perdas"]
    df_perdas = df_perdas[
        (df_perdas["data"].dt.year == ano) &
        (df_perdas["data"].dt.month == mes)
    ]

    df_perdas = df_perdas.groupby("motivo")["qtd"].count().reset_index()

    fig_perdas = px.pie(
        df_perdas,
        names="motivo",
        values="qtd",
        title="Distribuição de Perdas"
    )

    st.plotly_chart(fig_perdas, use_container_width=True)