import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

from data.loader import carregar_dados
from utils.tratamento import tratar_dados
from services.analises import faturamento_por_mes
from services.calculos import calcular_metricas


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard Scada Café",
    layout="wide"
)


# =========================
# CARREGAR DADOS
# =========================
dados = carregar_dados()
dados = tratar_dados(dados)


hoje = datetime.today()
ano_atual = hoje.year
mes_atual = hoje.month

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")

anos = sorted(dados["base_fat"]["ano"].dropna().unique())
ano = st.sidebar.selectbox(
    "Ano",
    anos,
    index=anos.index(ano_atual) if ano_atual in anos else 0
)

lista_meses = list(range(1, 13))

meses_dict = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

lista_meses_nomes = list(meses_dict.values())

mes_nome = st.sidebar.selectbox(
    "Mês",
    lista_meses_nomes,
    index=mes_atual - 1
)

# Converter nome do mês para número
mes = [k for k, v in meses_dict.items() if v == mes_nome][0]

st.title(f"📊 Dashboard Scada Café - {mes_nome} {ano}")
st.markdown("---")

# =========================
# FILTROS AVANÇADOS
# =========================
produtos = dados["base_produtos"]["produto"].dropna().unique()
produto_sel = st.sidebar.selectbox("Produto", ["Todos"] + list(produtos))

equipes = dados["base_fat"]["equipe"].dropna().unique()
equipe_sel = st.sidebar.selectbox("Equipe", ["Todas"] + list(equipes))

# =========================
# MÉTRICAS
# =========================
metricas = calcular_metricas(dados, ano, mes)

atingiu_meta = metricas["perc_meta"] >= 1
cor_meta = "normal" if atingiu_meta else "inverse"

# =========================
# ABAS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visão Geral",
    "📈 Faturamento",
    "📌 Projeções",
    "⚠️ Perdas",
    "🏆 Produtos",
])


# ======================================================
# 📊 VISÃO GERAL
# ======================================================
with tab1:

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Faturamento", f"R$ {metricas['total_fat']:,.2f}")
    col2.metric("Meta", f"R$ {metricas['meta']:,.2f}")

    col3.metric(
        "% Meta",
        f"{metricas['perc_meta']:.0%}",
        delta="Meta atingida" if atingiu_meta else "Abaixo da meta",
        delta_color=cor_meta
    )

    col4.metric("Ticket Médio", f"R$ {metricas['ticket_medio']:,.2f}")

    col5.metric(
       "Média Cupons",
        f"{metricas['media_cupons']:.0f}"
    )

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

        mes_ant = mes - 1 if mes > 1 else 12
        metricas_ant = calcular_metricas(dados, ano, mes_ant)

        delta = metricas["total_fat"] - metricas_ant["total_fat"]

        st.metric(
            "Faturamento Atual",
            f"R$ {metricas['total_fat']:,.2f}",
            delta=f"{delta:,.2f}"
        )

    # Insight
    st.markdown("### 🔍 Insight automático")

    if metricas["perc_meta"] >= 1:
        st.success("Meta atingida! Excelente performance.")
    elif metricas["perc_meta"] >= 0.9:
        st.warning("Próximo da meta.")
    else:
        st.error("Abaixo da meta. Atenção necessária.")


# ======================================================
# 📈 FATURAMENTO
# ======================================================
with tab2:

    st.subheader("📈 Evolução do Faturamento")

    df_fat = faturamento_por_mes(dados, ano)

    meses_dict = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    df_fat["mes_nome"] = df_fat["mes"].map(meses_dict)

    # Drill Down
    st.markdown("### 🔎 Drill-down por mês")

    meses_disponiveis = df_fat["mes"].tolist()

    mes_selecionado = st.selectbox(
        "Selecione um mês para análise detalhada",
        meses_disponiveis,
        index=meses_disponiveis.index(mes) if mes in meses_disponiveis else 0
    )

    #Gráfico
    fig_fat = px.bar(
        df_fat,
        x="mes_nome",
        y="faturamento",
        text="faturamento"
    )

    fig_fat.update_traces(texttemplate="R$ %{text:,.0f}")

    # Filtro base
    df_dia = dados["base_fat"].copy()

    df_dia = df_dia[
        (df_dia["ano"] == ano) &
        (df_dia["mes"] == mes_selecionado)
    ]

    # Filtro equipe
    if equipe_sel != "Todas":
        df_dia = df_dia[df_dia["equipe"] == equipe_sel]

    df_dia = (
        df_dia
        .groupby(df_dia["data"].dt.day)
        .agg({
            "faturamento": "sum",
            "ticket_medio": "mean",
            "cupom": "sum"
        })
        .reset_index()
    )

    # Remover dias com faturamento zero (dias futuros)
    df_dia = df_dia[df_dia["faturamento"] > 0]

    fig_dia = px.line(
        df_dia,
        x="data",
        y="faturamento",
        markers=True
    )

    fig_dia.update_layout(
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_fat, use_container_width=True)

    with col2:
        st.plotly_chart(fig_dia, use_container_width=True)


    st.markdown("### 📋 Dados de Faturamento")

    st.dataframe(df_dia, use_container_width=True)

    buffer_fat = io.BytesIO()
    df_dia.to_excel(buffer_fat, index=False)
    buffer_fat.seek(0)

    st.download_button(
        label="📥 Baixar Faturamento",
        data=buffer_fat,
        file_name="faturamento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ======================================================
# 📌 PROJEÇÕES
# ======================================================
with tab3:

    st.subheader("📌 Projeções de Meta")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Meta do Mês",
        f"R$ {metricas['meta']:,.2f}"
    )

    col2.metric(
        "Projeção Faturamento",
        f"R$ {metricas['proj_fat']:,.2f}"
    )

    col3.metric(
        "Faturamento Diário Necessário",
        f"R$ {metricas['fat_dia_necessario']:,.2f}"
    )

    col4.metric(
        "Ticket Médio Necessário",
        f"R$ {metricas['ticket_necessario']:,.2f}"
    )

    col5.metric(
        "Dias Restantes",
        f"{metricas['dias_restantes']}"
    )

    st.markdown("---")

    # Insight automático
    if metricas["proj_fat"] >= metricas["meta"]:
        st.success("Mantendo o ritmo atual, a meta será atingida.")
    else:
        st.error("No ritmo atual, a meta NÃO será atingida.")

    # GRÁFICOS
    st.markdown("### 📈 Ticket Médio x Cupons por Dia")

    df_plot = dados["base_fat"].copy()

    df_plot = df_plot[
        (df_plot["ano"] == ano) &
        (df_plot["mes"] == mes)
    ]

    # Ticket médio por dia
    ticket_dia = (
        df_plot.groupby(df_plot["data"].dt.day)["ticket_medio"]
        .mean()
        .reset_index()
    )

    # Cupons por dia
    cupons_dia = (
        df_plot.groupby(df_plot["data"].dt.day)["cupom"]
        .sum()
        .reset_index()
    )

    # Criar figura
    fig = go.Figure()

    # Linha 1 - Ticket médio
    fig.add_trace(
        go.Scatter(
            x=ticket_dia["data"],
            y=ticket_dia["ticket_medio"],
            mode="lines+markers",
            name="Ticket Médio",
            yaxis="y1"
        )
    )

    # Linha 2 - Cupons
    fig.add_trace(
        go.Scatter(
            x=cupons_dia["data"],
            y=cupons_dia["cupom"],
            mode="lines+markers",
            name="Cupons",
            yaxis="y2"
        )
    )

    # Layout com dois eixos
    fig.update_layout(
        yaxis=dict(title="Ticket Médio"),
        yaxis2=dict(
            title="Cupons",
            overlaying="y",
            side="right"
        ),
        xaxis=dict(title="Dia do Mês"),
        legend=dict(x=0.01, y=0.99),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


# ======================================================
# ⚠️ PERDAS
# ======================================================
with tab4:

    st.subheader("⚠️ Perdas")

    df_perdas = dados["base_perdas"].copy()

    df_perdas = df_perdas[
        (df_perdas["data"].dt.year == ano) &
        (df_perdas["data"].dt.month == mes)
    ]

    df_perdas = df_perdas.groupby("motivo")["qtd"].count().reset_index()

    fig_perdas = px.pie(
        df_perdas,
        names="motivo",
        values="qtd"
    )

    st.plotly_chart(fig_perdas, use_container_width=True)

    st.markdown("### 📋 Dados de Perdas")

    st.dataframe(df_perdas, use_container_width=True)

    st.markdown("### 📈 Evolução de Perdas no Ano")

    # Dados Mês a Mês
    df_perdas_ano = dados["base_perdas"].copy()

    df_perdas_ano = df_perdas_ano[
        df_perdas_ano["data"].dt.year == ano
    ]

    df_perdas_ano = (
        df_perdas_ano
        .groupby(df_perdas_ano["data"].dt.month)["qtd"]
        .count()
        .reset_index()
    )

    df_perdas_ano.rename(columns={"data": "mes"}, inplace=True)

    # Nome dos meses
    meses_dict = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    df_perdas_ano["mes_nome"] = df_perdas_ano["mes"].map(meses_dict)

    # Gráfico
    fig_perdas_mes = px.line(
        df_perdas_ano,
        x="mes_nome",
        y="qtd",
        markers=True,
        title="Perdas por Mês"
    )

    fig_perdas_mes.update_layout(
        xaxis_title="Mês",
        yaxis_title="Quantidade de Perdas"
    )

    st.plotly_chart(fig_perdas_mes, use_container_width=True)


# ======================================================
# 🏆 PRODUTOS
# ======================================================
with tab5:

    st.subheader("🏆 Produtos")

    df_prod = dados["base_produtos"].copy()

    df_prod = df_prod[df_prod["ano"] == ano]

    if produto_sel != "Todos":
        df_prod = df_prod[df_prod["produto"] == produto_sel]

    df_prod = df_prod.groupby("produto")["qtd"].sum().reset_index()
    df_prod = df_prod.sort_values("qtd", ascending=False).head(10)

    fig_prod = px.bar(
        df_prod,
        x="qtd",
        y="produto",
        orientation="h",
        text="qtd"
    )

    st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown("### 📋 Dados detalhados")

    st.dataframe(
        df_prod,
        use_container_width=True
    )


    # Converter para Excel em memória
    buffer_prod = io.BytesIO()
    df_prod.to_excel(buffer_prod, index=False)
    buffer_prod.seek(0)

    st.download_button(
        label="📥 Baixar Excel",
        data=buffer_prod,
        file_name="produtos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

