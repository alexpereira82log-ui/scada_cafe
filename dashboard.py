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

    st.subheader("📈 Evolução do Faturamento")

    df_fat = faturamento_por_mes(dados, ano)

    meses_dict = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    df_fat["mes_nome"] = df_fat["mes"].map(meses_dict)

    # =========================
    # DRILL DOWN
    # =========================
    st.markdown("### 🔎 Drill-down por mês")

    meses_disponiveis = df_fat["mes"].tolist()

    mes_selecionado = st.selectbox(
        "Selecione um mês para análise detalhada",
        meses_disponiveis,
        index=meses_disponiveis.index(mes) if mes in meses_disponiveis else 0
    )

    # =========================
    # GRÁFICOS PRINCIPAIS
    # =========================
    fig_fat = go.Figure()

    # 🔹 Meta (fundo)
    fig_fat.add_bar(
        x=df_fat["mes_nome"],
        y=df_fat["meta"],
        name="Meta",
        marker_color="lightgray",
        opacity=0.6
    )

    # 🔹 Faturamento (frente)
    fig_fat.add_bar(
        x=df_fat["mes_nome"],
        y=df_fat["faturamento"],
        name="Faturamento",
        text=df_fat["faturamento"],
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    # 🔹 Layout overlay
    fig_fat.update_layout(
        barmode="overlay",
        title="Faturamento vs Meta",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)"
    )

    fig_fat.update_traces(texttemplate="R$ %{text:,.0f}")

    # Base diária
    # 🔽 SOMENTE O TRECHO ALTERADO (para não poluir)
    # Vá direto na aba FATURAMENTO e substitua apenas este bloco:

    df_dia = dados["base_fat"].copy()

    df_dia = df_dia[
        (df_dia["ano"] == ano) &
        (df_dia["mes"] == mes_selecionado)
    ]

    if equipe_sel != "Todas":
        df_dia = df_dia[df_dia["equipe"] == equipe_sel]

    # 🔥 CORREÇÃO AQUI
    df_dia = (
        df_dia
        .groupby(df_dia["data"].dt.day)
        .agg({
            "faturamento": "sum",
            "cupom": "sum"
        })
        .reset_index()
    )

    # 🔥 cálculo correto do ticket médio
    df_dia["ticket_medio"] = df_dia.apply(
        lambda x: x["faturamento"] / x["cupom"] if x["cupom"] > 0 else 0,
        axis=1
    )

    # manter apenas dias válidos
    df_dia = df_dia[df_dia["faturamento"] > 0]



    fig_dia = px.line(
        df_dia,
        x="data",
        y="faturamento",
        markers=True,
        title="Faturamento Diário"
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

    # =========================
    # TABELA
    # =========================
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

    # =========================
    # YOY
    # =========================
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
        markers=True,
        title="Comparação Ano a Ano"
    )

    st.plotly_chart(fig_yoy, use_container_width=True)

    # =========================
    # YTD
    # =========================
    st.markdown("### 📈 Acumulado no Ano (YTD)")

    df_ytd = dados["base_fat"].copy()

    df_ytd = df_ytd[df_ytd["ano"].isin([ano, ano - 1])]

    df_ytd = (
        df_ytd
        .groupby([df_ytd["data"].dt.month, "ano"])["faturamento"]
        .sum()
        .reset_index()
    )

    df_ytd.rename(columns={"data": "mes"}, inplace=True)

    df_ytd = df_ytd[df_ytd["mes"] <= mes]

    df_ytd = df_ytd.sort_values(["ano", "mes"])

    df_ytd["acumulado"] = df_ytd.groupby("ano")["faturamento"].cumsum()

    df_ytd["mes_nome"] = df_ytd["mes"].map(meses_dict)

    fig_ytd = px.line(
        df_ytd,
        x="mes_nome",
        y="acumulado",
        color="ano",
        markers=True,
        title="Faturamento Acumulado (YTD)"
    )

    st.plotly_chart(fig_ytd, use_container_width=True)

    # =========================
    # 📊 TICKET MÉDIO x CUPONS (MENSAL)
    # =========================
    st.markdown("### 📊 Ticket Médio x Cupons (Mensal)")

    df_tc = dados["base_fat"].copy()

    # filtrar apenas ano atual
    df_tc = df_tc[df_tc["ano"] == ano]

    # 🔥 apenas até o mês atual selecionado
    df_tc = df_tc[df_tc["mes"] <= mes]

    # =========================
    # AGRUPAMENTO MENSAL CORRETO
    # =========================
    df_tc = (
        df_tc
        .groupby("mes")
        .agg({
            "faturamento": "sum",
            "cupom": "sum"
        })
        .reset_index()
    )

    # 🔥 ticket médio correto (NÃO média)
    df_tc["ticket_medio"] = df_tc.apply(
        lambda x: x["faturamento"] / x["cupom"] if x["cupom"] > 0 else 0,
        axis=1
    )

    # 🔥 média de cupons por dia no mês
    df_tc["cupons_medios"] = (
        dados["base_fat"]
        .copy()
        .query("ano == @ano")
        .query("mes <= @mes")
        .groupby("mes")["cupom"]
        .mean()
        .values
    )

    # nomes dos meses
    meses_dict = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    df_tc["mes_nome"] = df_tc["mes"].map(meses_dict)

    # =========================
    # GRÁFICO
    # =========================
    fig_tc = go.Figure()

    # Ticket médio
    fig_tc.add_trace(
        go.Scatter(
            x=df_tc["mes_nome"],
            y=df_tc["ticket_medio"],
            mode="lines+markers",
            name="Ticket Médio",
            yaxis="y1"
        )
    )

    # Cupons médios
    fig_tc.add_trace(
        go.Scatter(
            x=df_tc["mes_nome"],
            y=df_tc["cupons_medios"],
            mode="lines+markers",
            name="Cupons Médios",
            yaxis="y2"
        )
    )

    # layout
    fig_tc.update_layout(
        title="Ticket Médio x Cupons por Mês",
        xaxis_title="Mês",
        yaxis=dict(title="Ticket Médio (R$)"),
        yaxis2=dict(
            title="Cupons Médios",
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.01, y=0.99),
        height=400
    )

    st.plotly_chart(fig_tc, use_container_width=True)


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
# 🏆 PRODUTOS
# ======================================================
with tab5:

    st.subheader("📊 Performance de Produtos")

    df = dados["base_produtos"].copy()

    # =========================
    # FILTRO
    # =========================
    df = df[
        (df["ano"] == ano) &
        (df["mes"] == mes)
    ]

    if df.empty:
        st.warning("Sem dados de produtos para o período selecionado.")
    else:

        # =========================
        # AGRUPAMENTO
        # =========================
        df_prod = (
            df
            .groupby("produto")
            .agg({
                "qtd": "sum",
                "valor_total": "sum"
            })
            .reset_index()
            .sort_values("valor_total", ascending=False)
        )

        # =========================
        # RANKING
        # =========================
        st.markdown("### 🏆 Ranking de Produtos")

        st.dataframe(
            df_prod.head(10),
            use_container_width=True
        )

        # =========================
        # GRÁFICO TOP PRODUTOS
        # =========================
        import plotly.express as px

        fig_top = px.bar(
            df_prod.head(10),
            x="valor_total",
            y="produto",
            orientation="h",
            text="valor_total"
        )

        fig_top.update_traces(texttemplate="R$ %{text:,.0f}")
        fig_top.update_layout(yaxis=dict(autorange="reversed"))

        st.plotly_chart(fig_top, use_container_width=True)

        # =========================
        # CURVA ABC
        # =========================
        st.markdown("### 📈 Curva ABC")

        df_prod["perc_acumulado"] = (
            df_prod["valor_total"].cumsum() /
            df_prod["valor_total"].sum()
        )

        def classificar_abc(p):
            if p <= 0.8:
                return "A"
            elif p <= 0.95:
                return "B"
            else:
                return "C"

        df_prod["classe"] = df_prod["perc_acumulado"].apply(classificar_abc)

        fig_abc = px.line(
            df_prod,
            x=range(len(df_prod)),
            y="perc_acumulado"
        )

        st.plotly_chart(fig_abc, use_container_width=True)

        st.dataframe(
            df_prod[["produto", "valor_total", "classe"]],
            use_container_width=True
        )

        # =========================
        # INSIGHTS AUTOMÁTICOS
        # =========================
        st.markdown("### 🧠 Insights Automáticos")

        top1 = df_prod.iloc[0]

        perc_top1 = top1["valor_total"] / df_prod["valor_total"].sum()

        insights = []

        if perc_top1 > 0.25:
            insights.append("Alta dependência de um único produto.")

        if len(df_prod[df_prod["classe"] == "A"]) < 5:
            insights.append("Poucos produtos representam a maior parte da receita.")

        if df_prod["qtd"].mean() < 5:
            insights.append("Baixo volume médio de vendas por produto.")

        if not insights:
            insights.append("Mix de produtos equilibrado.")

        for i in insights:
            st.info(i)


# ======================================================
# 📄 RELATÓRIO VENDAS
# ======================================================
with tab6:

    st.write("🚀 Entrou na aba 6")

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