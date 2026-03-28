import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

# =========================
# CARREGAR DADOS
# =========================
dados = carregar_dados()
dados = tratar_dados(dados)

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")

anos = sorted(dados["base_fat"]["data"].dt.year.unique())
ano = st.sidebar.selectbox("Selecione o Ano", anos)

meses = list(range(1, 13))
mes = st.sidebar.selectbox("Selecione o Mês", meses)

# =========================
# MÉTRICAS
# =========================
metricas = calcular_metricas(dados, ano, mes)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Faturamento", f"R$ {metricas['total_fat']:,.2f}")
col2.metric("Meta", f"R$ {metricas['meta']:,.2f}")
col3.metric("% Meta", f"{metricas['perc_meta']:.0%}")
col4.metric("Ticket Médio", f"R$ {metricas['ticket_medio']:,.2f}")

# =========================
# GRÁFICO FATURAMENTO
# =========================
st.subheader("Faturamento por Mês")

df_fat = faturamento_por_mes(dados, ano)

fig, ax = plt.subplots()
ax.bar(df_fat["mes"], df_fat["faturamento"])
ax.set_title("Faturamento Mensal")

st.pyplot(fig)

# =========================
# TOP PRODUTOS
# =========================
st.subheader("Top Produtos")

df_prod = top_produtos(dados, ano)

st.dataframe(df_prod.head(10))