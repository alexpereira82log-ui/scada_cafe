import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io


from data.loader import carregar_dados
from data.tratamento import tratar_dados
from services.analises import (
    faturamento_por_mes,
    analise_dia_semana
)
from data.drive_loader import conectar_drive, listar_arquivos, baixar_arquivo
from services.relatorios import extrair_indicadores
from services.calculos import calcular_metricas
from datetime import datetime
from services.insights import gerar_insights
from services.relatorios import extrair_vendas_por_hora
from services.relatorios import extrair_produtos_relatorio
from services.analises import resumo_faturamento


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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Visão Geral",
    "📈 Faturamento",
    "📌 Projeções",
    "⚠️ Perdas",
    "🏆 Produtos",
    "📄 Relatório Vendas"
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

        st.subheader("📊 Comparação Anual")

        # Faturamento atual
        fat_atual = metricas["total_fat"]

        # Faturamento ano anterior (mesmo mês)
        metricas_ano_ant = calcular_metricas(dados, ano - 1, mes)
        fat_ano_ant = metricas_ano_ant["total_fat"]

        # Cálculo percentual
        if fat_ano_ant > 0:
            crescimento = (fat_atual - fat_ano_ant) / fat_ano_ant
        else:
            crescimento = 0

        # Definir cor e texto
        delta_valor = crescimento  # valor numérico

        st.metric(
            "Faturamento Atual",
            f"R$ {fat_atual:,.2f}",
            delta=f"{delta_valor:.1%}",
        )

        # Exibir comparativo
        st.markdown(f"""
        📅 Mesmo mês ano anterior: **R$ {fat_ano_ant:,.2f}**
        """)

    # Insight
    st.markdown("### 🧠 Insights Inteligentes")

    insights = gerar_insights(dados, metricas, ano, mes)

    for tipo, _, mensagem in insights:

        if tipo == "sucesso":
            st.success(mensagem)

        elif tipo == "alerta":
            st.warning(mensagem)

        elif tipo == "erro":
            st.error(mensagem)


# ======================================================
# 📈 FATURAMENTO
# ======================================================
with tab2:

    # =========================================
    # 📈 EVOLUÇÃO DO FATURAMENTO
    # =========================================

    st.subheader("📈 Evolução do Faturamento")

    df_fat = faturamento_por_mes(dados, ano)

    meses_dict = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    df_fat["mes_nome"] = df_fat["mes"].map(meses_dict)

    # =========================================
    # DRILL DOWN
    # =========================================
    st.markdown("### 🔎 Drill-down por mês")

    meses_disponiveis = df_fat["mes"].tolist()

    mes_selecionado = st.selectbox(
        "Selecione um mês para análise detalhada",
        meses_disponiveis,
        index=meses_disponiveis.index(mes) if mes in meses_disponiveis else 0
    )

    # =========================================
    # GRÁFICO FATURAMENTO
    # =========================================
    fig_fat = go.Figure()

    fig_fat.add_bar(
        x=df_fat["mes_nome"],
        y=df_fat["meta"],
        name="Meta",
        marker_color="lightgray",
        opacity=0.6
    )

    fig_fat.add_bar(
        x=df_fat["mes_nome"],
        y=df_fat["faturamento"],
        name="Faturamento",
        text=df_fat["faturamento"],
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    fig_fat.update_layout(
        barmode="overlay",
        title="Faturamento vs Meta"
    )

    # =========================================
    # BASE DIÁRIA (CORRIGIDA)
    # =========================================
    df_dia = dados["base_fat"].copy()

    df_dia = df_dia[
        (df_dia["ano"] == ano) &
        (df_dia["mes"] == mes_selecionado)
    ]

    if equipe_sel != "Todas":
        df_dia = df_dia[df_dia["equipe"] == equipe_sel]

    df_dia = (
        df_dia
        .groupby("data")
        .agg({
            "faturamento": "sum",
            "cupom": "sum"
        })
        .reset_index()
    )

    # =========================
    # REMOVER DIAS SEM FATURAMENTO
    # =========================
    df_dia = df_dia[df_dia["faturamento"] > 0]

    # =========================
    # FORMATAR DIA (01, 02, 03...)
    # =========================
    df_dia["dia"] = df_dia["data"].dt.strftime("%d")

    # =========================
    # TICKET MÉDIO
    # =========================
    df_dia["ticket_medio"] = df_dia.apply(
        lambda x: x["faturamento"] / x["cupom"] if x["cupom"] > 0 else 0,
        axis=1
    )

    # =========================================
    # GRÁFICO DIÁRIO
    # =========================================
    fig_dia = px.line(
        df_dia,
        x="dia",
        y="faturamento",
        markers=True,
        title="Faturamento Diário"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_fat, use_container_width=True)

    with col2:
        st.plotly_chart(fig_dia, use_container_width=True)


    # =========================================
    # 📊 RESUMO EXECUTIVO (TOPO)
    # =========================================

    st.markdown("### 🔎 Análise por Equipe")

    df = dados["base_fat"].copy()

    df = df[
        (df["ano"] == ano) &
        (df["mes"] == mes)
    ]

    if not df.empty:

        # =========================
        # GERAL
        # =========================
        fat_medio, ticket, cupons_medio = resumo_faturamento(df)

        # =========================
        # EQUIPE 1
        # =========================
        df_eq1 = df[df["equipe"] == 1]
        fat1, ticket1, cup1 = resumo_faturamento(df_eq1)

        # =========================
        # EQUIPE 2
        # =========================
        df_eq2 = df[df["equipe"] == 2]
        fat2, ticket2, cup2 = resumo_faturamento(df_eq2)

        # =========================
        # LINHA 1 (GERAL)
        # =========================
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<p style='font-size:18px'><b>Faturamento Médio</b><br>R$ {fat_medio:,.2f}</p>", unsafe_allow_html=True)
        col2.markdown(f"<p style='font-size:18px'><b>Ticket Médio</b><br>R$ {ticket:,.2f}</p>", unsafe_allow_html=True)
        col3.markdown(f"<p style='font-size:18px'><b>Cupons/Dia</b><br>{cupons_medio:,.0f}</p>", unsafe_allow_html=True)

        # =========================
        # LINHA 2 (EQUIPE 1)
        # =========================
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<p style='font-size:14px'>Equipe 1<br>R$ {fat1:,.2f}</p>", unsafe_allow_html=True)
        col2.markdown(f"<p style='font-size:14px'>Equipe 1<br>R$ {ticket1:,.2f}</p>", unsafe_allow_html=True)
        col3.markdown(f"<p style='font-size:14px'>Equipe 1<br>{cup1:,.0f}</p>", unsafe_allow_html=True)

        # =========================
        # LINHA 3 (EQUIPE 2)
        # =========================
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<p style='font-size:14px'>Equipe 2<br>R$ {fat2:,.2f}</p>", unsafe_allow_html=True)
        col2.markdown(f"<p style='font-size:14px'>Equipe 2<br>R$ {ticket2:,.2f}</p>", unsafe_allow_html=True)
        col3.markdown(f"<p style='font-size:14px'>Equipe 2<br>{cup2:,.0f}</p>", unsafe_allow_html=True)

        st.markdown("---")


    # =========================================
    # TABELA
    # =========================================
    st.markdown("### 📋 Dados de Faturamento")

    df_dia["data"] = df_dia["data"].dt.strftime("%Y-%m-%d")
    st.dataframe(df_dia, use_container_width=True)

    buffer = io.BytesIO()
    df_dia.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        "📥 Baixar Faturamento",
        buffer,
        "faturamento.xlsx"
    )

    # =========================================
    # YOY
    # =========================================
    st.markdown("### 📊 Comparação Ano a Ano (YoY)")

    df_yoy = dados["base_fat"].copy()

    df_yoy = df_yoy[df_yoy["ano"].isin([ano, ano - 1])]

    df_yoy = (
        df_yoy
        .groupby([df_yoy["data"].dt.month, "ano"])["faturamento"]
        .sum()
        .reset_index()
    )

    df_yoy.rename(columns={"data": "mes"}, inplace=True)

    df_yoy["mes_nome"] = df_yoy["mes"].map(meses_dict)

    fig_yoy = px.line(
        df_yoy,
        x="mes_nome",
        y="faturamento",
        color="ano",
        markers=True
    )

    st.plotly_chart(fig_yoy, use_container_width=True)


    # =========================================
    # ⏱️ VENDAS POR HORA (MÉDIA DO MÊS)
    # =========================================
    st.markdown("### ⏱️ Vendas por Hora (Média do Mês)")

    service = conectar_drive()
    FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"
    arquivos = listar_arquivos(service, FOLDER_ID)

    dfs = []

    if arquivos:

        for arq in arquivos:

            nome = arq["name"]

            # 🔥 filtrar pelo mês selecionado
            if f"{ano}-{str(mes).zfill(2)}" in nome:

                texto = baixar_arquivo(service, arq["id"])

                df_temp = extrair_vendas_por_hora(texto)

                if not df_temp.empty:
                    dfs.append(df_temp)

        if dfs:

            df_total = pd.concat(dfs)

            # =========================
            # MÉDIA POR HORA
            # =========================
            df_media = (
                df_total
                .groupby("hora")
                .agg({
                    "faturamento": "mean",
                    "cupons": "mean",
                    "ticket": "mean"
                })
                .reset_index()
            )

            # =========================
            # GRÁFICO 1
            # =========================
            fig_hora = px.bar(
                df_media,
                x="hora",
                y="faturamento",
                title="Faturamento Médio por Hora"
            )

            fig_hora.update_layout(
                xaxis=dict(
                    tickmode='linear',
                    dtick=1
                )
            )
            
            st.plotly_chart(fig_hora, use_container_width=True)

            # =========================
            # GRÁFICO 2
            # =========================
            fig2 = go.Figure()

            # =========================
            # BARRAS - CUPONS
            # =========================
            fig2.add_trace(
                go.Bar(
                    x=df_media["hora"],
                    y=df_media["cupons"],
                    name="Cupons",
                    yaxis="y1"
                )
            )

            # =========================
            # LINHA - TICKET
            # =========================
            fig2.add_trace(
                go.Scatter(
                    x=df_media["hora"],
                    y=df_media["ticket"],
                    mode="lines+markers",
                    name="Ticket Médio",
                    yaxis="y2"
                )
            )

            # =========================
            # LAYOUT
            # =========================
            fig2.update_layout(
                title="Ticket Médio x Cupons por Hora (Média do Mês)",
                xaxis=dict(
                    tickmode='linear',
                    dtick=1
                ),
                yaxis=dict(title="Cupons"),
                yaxis2=dict(
                    title="Ticket Médio (R$)",
                    overlaying="y",
                    side="right"
                )
            )

            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.warning("Nenhum relatório do mês encontrado.")

    else:
        st.warning("Nenhum relatório encontrado.")


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

    # =========================
    # BASE CORRETA
    # =========================
    df_plot = (
        df_plot
        .groupby(df_plot["data"].dt.day)
        .agg({
            "faturamento": "sum",
            "cupom": "sum"
        })
        .reset_index()
    )

    # 🔥 remover dias sem faturamento
    df_plot = df_plot[df_plot["faturamento"] > 0]

    # 🔥 ticket médio correto
    df_plot["ticket_medio"] = df_plot.apply(
        lambda x: x["faturamento"] / x["cupom"] if x["cupom"] > 0 else 0,
        axis=1
    )

    # Criar figura
    fig = go.Figure()

    # Ticket médio
    fig.add_trace(
        go.Scatter(
            x=df_plot["data"],
            y=df_plot["ticket_medio"],
            mode="lines+markers",
            name="Ticket Médio",
            yaxis="y1"
        )
    )

    # Cupons
    fig.add_trace(
        go.Scatter(
            x=df_plot["data"],
            y=df_plot["cupom"],
            mode="lines+markers",
            name="Cupons",
            yaxis="y2"
        )
    )

    # Layout com dois eixos
    fig.update_layout(
        title="Ticket Médio x Cupons por Dia",
        xaxis_title="Dia do Mês",
        yaxis=dict(title="Ticket Médio (R$)"),
        yaxis2=dict(
            title="Cupons",
            overlaying="y",
            side="right"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # ANALISE DIA DA SEMANA
    # =========================
    st.markdown("### 📊 Resultado por Dia da Semana")

    df_semana = analise_dia_semana(dados, ano)

    st.dataframe(df_semana, use_container_width=True)


    # =========================================
    # 📊 TICKET MÉDIO x CUPONS POR MÊS
    # =========================================
    st.markdown("### 📊 Ticket Médio x Cupons por Mês")

    df_mes = dados["base_fat"].copy()

    df_mes = df_mes[
        (df_mes["ano"] == ano) &
        (df_mes["mes"] <= mes)
    ]

    # Agrupar por mês
    df_mes = (
        df_mes
        .groupby("mes")
        .agg({
            "faturamento": "sum",
            "cupom": "sum",
            "data": "nunique"
        })
        .reset_index()
    )

    # Métricas
    df_mes["ticket_medio"] = df_mes["faturamento"] / df_mes["cupom"]
    df_mes["cupons_dia"] = df_mes["cupom"] / df_mes["data"]

    # Nome dos meses
    meses_dict = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    df_mes["mes_nome"] = df_mes["mes"].map(meses_dict)

    # Gráfico
    fig = go.Figure()

    # Ticket médio
    fig.add_trace(
        go.Scatter(
            x=df_mes["mes_nome"],
            y=df_mes["ticket_medio"],
            mode="lines+markers",
            name="Ticket Médio",
            yaxis="y1"
        )
    )

    # Cupons/dia
    fig.add_trace(
        go.Scatter(
            x=df_mes["mes_nome"],
            y=df_mes["cupons_dia"],
            mode="lines+markers",
            name="Cupons/Dia",
            yaxis="y2"
        )
    )

    fig.update_layout(
        title="Ticket Médio x Cupons por Mês",
        yaxis=dict(title="Ticket Médio (R$)"),
        yaxis2=dict(
            title="Cupons/Dia",
            overlaying="y",
            side="right"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================================
    # 📈 FATURAMENTO ACUMULADO (ANO)
    # =========================================
    st.markdown("### 📈 Faturamento Acumulado no Ano")

    df_acum = dados["base_fat"].copy()

    df_acum = df_acum[
        df_acum["ano"].isin([ano, ano - 1])
    ]

    # Agrupar por mês
    df_acum = (
        df_acum
        .groupby(["ano", "mes"])["faturamento"]
        .sum()
        .reset_index()
    )

    # Ordenar
    df_acum = df_acum.sort_values(["ano", "mes"])

    # Acumulado
    df_acum["faturamento_acum"] = df_acum.groupby("ano")["faturamento"].cumsum()

    # Filtrar até mês atual
    df_acum = df_acum[df_acum["mes"] <= mes]

    # Nome meses
    df_acum["mes_nome"] = df_acum["mes"].map(meses_dict)

    # Gráfico
    fig_acum = px.line(
        df_acum,
        x="mes_nome",
        y="faturamento_acum",
        color="ano",
        markers=True,
        title="Faturamento Acumulado (Ano vs Ano Anterior)"
    )

    st.plotly_chart(fig_acum, use_container_width=True)

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

    st.markdown("### 📋 Perdas por Motivo")

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


    # =========================
    # 📋 TABELA DETALHADA DE PERDAS (MÊS)
    # =========================

    st.markdown("### 📋 Detalhamento de Perdas do Mês")

    df_perdas_detalhe = dados["base_perdas"].copy()

    # Filtro por ano e mês
    df_perdas_detalhe = df_perdas_detalhe[
        (df_perdas_detalhe["data"].dt.year == ano) &
        (df_perdas_detalhe["data"].dt.month == mes)
    ]

    # Ordenar por data decrescente
    df_perdas_detalhe = df_perdas_detalhe.sort_values(
        by="data",
        ascending=False
    )

    # 🔥 Ajustar formato da data
    df_perdas_detalhe["data"] = df_perdas_detalhe["data"].dt.strftime("%Y-%m-%d")

    # Exibir tabela
    st.dataframe(df_perdas_detalhe, use_container_width=True)

 
    # 📥 Download Excel
    import io

    buffer = io.BytesIO()
    df_perdas_detalhe.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Baixar Perdas",
        data=buffer,
        file_name="perdas_mes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ======================================================
# 🏆 PRODUTOS (NOVA VERSÃO COMPLETA)
# ======================================================
with tab5:

    st.subheader("🏆 Análise de Produtos (Relatório Diário)")

    # =========================
    # MODO DE ANÁLISE
    # =========================
    modo = st.radio(
        "Modo de análise",
        ["📊 Acumulado", "📅 Dia específico"],
        horizontal=True
    )

    # =========================
    # CONEXÃO DRIVE
    # =========================
    service = conectar_drive()
    FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"
    arquivos = listar_arquivos(service, FOLDER_ID)

    if not arquivos:
        st.warning("Nenhum relatório encontrado.")
        st.stop()

    # =========================
    # 📊 MODO ACUMULADO
    # =========================
    if modo == "📊 Acumulado":

        lista_df = []

        for arq in arquivos:
            texto = baixar_arquivo(service, arq["id"])
            df_temp = extrair_produtos_relatorio(texto)

            if not df_temp.empty:
                lista_df.append(df_temp)

        if not lista_df:
            st.warning("Nenhum dado encontrado nos relatórios.")
            st.stop()

        df_prod = pd.concat(lista_df, ignore_index=True)

    # =========================
    # 📅 MODO DIA ESPECÍFICO
    # =========================
    else:

        nomes = [a["name"] for a in arquivos]

        arquivo_sel = st.selectbox(
            "Selecione o relatório",
            nomes,
            key="select_relatorio_produtos"
        )

        arquivo = next(a for a in arquivos if a["name"] == arquivo_sel)

        texto = baixar_arquivo(service, arquivo["id"])
        df_prod = extrair_produtos_relatorio(texto)

        if df_prod.empty:
            st.warning("Nenhum produto encontrado no relatório.")
            st.stop()

    # =========================
    # AGRUPAMENTO
    # =========================
    df_prod = (
        df_prod
        .groupby("produto")
        .agg({
            "qtd": "sum",
            "valor_total": "sum"
        })
        .reset_index()
        .sort_values("valor_total", ascending=False)
    )

    total = df_prod["valor_total"].sum()
    df_prod["participacao"] = df_prod["valor_total"] / total
    df_prod["perc"] = df_prod["participacao"] * 100

    # =========================
    # 🏆 TOP PRODUTOS
    # =========================
    st.markdown("### 🏆 Top Produtos")

    st.dataframe(
        df_prod.head(10),
        use_container_width=True
    )

    # =========================
    # 📊 GRÁFICO
    # =========================
    fig = px.bar(
        df_prod.head(10),
        x="valor_total",
        y="produto",
        orientation="h",
        text="valor_total"
    )

    fig.update_layout(yaxis=dict(autorange="reversed"))

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 📊 PARTICIPAÇÃO
    # =========================
    st.markdown("### 📊 Participação (%)")

    st.dataframe(
        df_prod[["produto", "valor_total", "perc"]],
        use_container_width=True
    )

    # =========================
    # 📈 CURVA ABC
    # =========================
    st.markdown("### 📈 Curva ABC")

    df_prod["perc_acum"] = df_prod["participacao"].cumsum()

    def classificar(p):
        if p <= 0.8:
            return "A"
        elif p <= 0.95:
            return "B"
        else:
            return "C"

    df_prod["classe"] = df_prod["perc_acum"].apply(classificar)

    st.dataframe(
        df_prod[["produto", "valor_total", "classe"]],
        use_container_width=True
    )

    # =========================
    # 🧠 INSIGHTS
    # =========================
    insights = []

    top1 = df_prod.iloc[0]
    perc_top1 = top1["participacao"]

    # Regra principal
    if perc_top1 > 0.25:
        insights.append("⚠️ Alta dependência de um único produto.")
    elif perc_top1 > 0.15:
        insights.append("🔎 Produto líder com boa relevância no faturamento.")
    else:
        insights.append("✅ Boa distribuição de vendas entre produtos.")

    # Curva ABC
    qtd_a = len(df_prod[df_prod["classe"] == "A"])

    if qtd_a < 5:
        insights.append("⚠️ Poucos produtos concentram a maior parte da receita.")
    elif qtd_a > 10:
        insights.append("📊 Mix amplo de produtos com impacto relevante.")

    # =========================
    # EXIBIÇÃO
    # =========================
    st.markdown("### 🧠 Insights")

    for i in insights:
        st.info(i)


# ======================================================
# 📄 RELATÓRIO VENDAS
# ======================================================
with tab6:

    st.subheader("📄 Relatório de Vendas")

    # =========================
    # 🔗 CONEXÃO COM DRIVE
    # =========================
    service = conectar_drive()

    FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"

    arquivos = listar_arquivos(service, FOLDER_ID)

    if not arquivos:
        st.warning("Nenhum relatório encontrado.")
    else:

        # =========================
        # 📅 ORDENAR ARQUIVOS (mais recente primeiro)
        # =========================
        arquivos = sorted(arquivos, key=lambda x: x["name"], reverse=True)

        nomes = [arq["name"] for arq in arquivos]

        arquivo_sel = st.selectbox("Selecione o relatório", nomes)

        # =========================
        # 📥 BAIXAR ARQUIVO
        # =========================
        file_id = next(arq["id"] for arq in arquivos if arq["name"] == arquivo_sel)

        texto = baixar_arquivo(service, file_id)

        # =========================
        # 📊 EXTRAÇÃO DE DADOS (BI)
        # =========================
        indicadores = extrair_indicadores(texto)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Faturamento", f"R$ {indicadores['faturamento_bruto']:,.0f}")
        col2.metric("Resultado", f"R$ {indicadores['resultado_operacional']:,.0f}")
        col3.metric("Ticket Médio", f"R$ {indicadores['ticket_medio']:,.0f}")
        col4.metric("Cupons", f"{indicadores['cupons']}")

        st.markdown("---")

        # =========================
        # 📄 RELATÓRIO COMPLETO
        # =========================
        with st.expander("📄 Ver relatório completo"):
            st.text(texto)