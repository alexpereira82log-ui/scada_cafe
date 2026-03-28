import streamlit as st
import pandas as pd
import plotly.express as px

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
# MÉTRICAS (KPIs)
# =========================
metricas = calcular_metricas(dados, ano, mes)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Faturamento", f"R$ {metricas['total_fat']:,.2f}")
col2.metric("Meta", f"R$ {metricas['meta']:,.2f}")
col3.metric("% Meta", f"{metricas['perc_meta']:.0%}")
col4.metric("Ticket Médio", f"R$ {metricas['ticket_medio']:,.2f}")

st.markdown("---")

# =========================
# 📈 SEÇÃO 1 — FATURAMENTO
# =========================
st.subheader("📈 Evolução do Faturamento")

df_fat = faturamento_por_mes(dados, ano)

fig_fat = px.bar(
    df_fat,
    x="mes",
    y="faturamento",
    text="faturamento",
)

fig_fat.update_traces(
    texttemplate="R$ %{text:,.0f}",
    textposition="outside"
)

fig_fat.update_layout(
    xaxis_title="Mês",
    yaxis_title="Faturamento",
    title="Faturamento Mensal"
)

# =========================
# FATURAMENTO DIÁRIO
# =========================
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

# 👉 AQUI usamos colunas (layout profissional)
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_fat, use_container_width=True)

with col2:
    st.plotly_chart(fig_dia, use_container_width=True)

st.markdown("---")

# =========================
# 🏆 SEÇÃO 2 — PRODUTOS
# =========================
st.subheader("🏆 Performance de Produtos")

df_prod = top_produtos(dados, ano).head(10)

fig_prod = px.bar(
    df_prod,
    x="produto",
    y="qtd",
    text="qtd",
    title="Top 10 Produtos"
)

fig_prod.update_traces(textposition="outside")

st.plotly_chart(fig_prod, use_container_width=True)

st.markdown("---")

# =========================
# ⚠️ SEÇÃO 3 — PERDAS
# =========================
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