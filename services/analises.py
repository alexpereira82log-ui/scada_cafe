# versão atualizada 1
import pandas as pd
from database.connection import get_connection


# ============================================================
# FATURAMENTO POR MÊS
# ============================================================
def faturamento_por_mes(dados: dict, ano: int) -> pd.DataFrame:
    df = dados["base_fat"]

    df_ano = df[df["ano"] == ano]

    resultado = (
        df_ano
        .groupby(["mes", "mes_nome"])[["faturamento", "meta"]]
        .sum()
        .reset_index()
        .sort_values("mes")
    )

    return resultado


# ============================================================
# FATURAMENTO POR DIA
# ============================================================
def faturamento_por_dia(dados: dict, ano: int, mes: int) -> pd.DataFrame:
    df = dados["base_fat"]

    df_mes = df[(df["ano"] == ano) & (df["mes"] == mes)]

    resultado = (
        df_mes
        .groupby("data")["faturamento"]
        .sum()
        .reset_index()
        .sort_values("data")
    )

    resultado = resultado[resultado["faturamento"] > 0]

    return resultado


# ============================================================
# TOP PRODUTOS
# ============================================================
def top_produtos(dados: dict, ano: int) -> pd.DataFrame:
    df = dados["base_produtos"]

    df_ano = df[df["ano"] == ano]

    resultado = (
        df_ano
        .groupby("produto")
        .agg({
            "qtd": "sum",
            "valor_total": "sum"
        })
        .reset_index()
        .sort_values("qtd", ascending=False)
    )

    return resultado


# ============================================================
# PERDAS POR MOTIVO
# ============================================================
def perdas_por_motivo(dados: dict, ano: int, mes: int) -> pd.DataFrame:
    df = dados["base_perdas"].copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    df_filtrado = df[
        (df["data"].dt.year == ano) &
        (df["data"].dt.month == mes)
    ]

    resultado = (
        df_filtrado
        .groupby("motivo")
        .size()  # 🔥 conta registros corretamente
        .reset_index(name="qtd")
        .sort_values("qtd", ascending=False)
    )

    return resultado


# ============================================================
# PERDAS POR MÊS
# ============================================================
def perdas_por_mes(dados: dict, ano: int) -> pd.DataFrame:
    df = dados["base_perdas"].copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    df_ano = df[df["data"].dt.year == ano].copy()

    df_ano["mes"] = df_ano["data"].dt.month

    meses_dict = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    df_ano["mes_nome"] = df_ano["mes"].map(meses_dict)

    resultado = (
        df_ano
        .groupby(["mes", "mes_nome"])["qtd"]
        .count()  # 🔥 AQUI ESTÁ A CORREÇÃO
        .reset_index()
        .rename(columns={"qtd": "qtd_registros"})
        .sort_values("mes")
    )

    return resultado


# ============================================================
# COMISSÃO POR COLABORADOR (MÊS)
# ============================================================
def comissao_por_colaborador(dados: dict, ano: int, mes: int) -> pd.DataFrame:
    df = dados["base_comissao"].copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    df_mes = df[
        (df["data"].dt.year == ano) &
        (df["data"].dt.month == mes)
    ]

    resultado = (
        df_mes
        .groupby("colaborador_id")["valor"]
        .sum()
        .reset_index()
        .sort_values("valor", ascending=False)
    )

    return resultado


# ============================================================
# COMISSÃO MES E PROJEÇÕES
# ============================================================
def calcular_comissao_projecoes(dados: dict, ano: int, mes: int, metricas: dict) -> dict:

    df = dados.get("base_comissao", pd.DataFrame()).copy()
    df_colab = dados.get("base_colaboradores", pd.DataFrame()).copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # Filtrar mês
    df_mes = df[
        (df["data"].dt.year == ano) &
        (df["data"].dt.month == mes)
    ]

    # ❌ Remover Brunna
    df_mes = df_mes[df_mes["colaborador_id"] != 1]

    if df_mes.empty or df_colab.empty:
        return {
            "df": pd.DataFrame(),
            "media": 0,
            "projecao": 0,
            "total_acumulado": 0
        }

    # =========================
    # TOTAL POR COLABORADOR
    # =========================
    df_group = (
        df_mes
        .groupby("colaborador_id")["valor"]
        .sum()
        .reset_index()
    )

    # Ajustar nomes
    df_colab = df_colab.rename(columns={"id": "colaborador_id"})

    df_group = df_group.merge(
        df_colab,
        on="colaborador_id",
        how="left"
    )

    df_group = df_group.sort_values("valor", ascending=False)

    df_group = df_group[["nome", "valor"]]

    # =========================
    # CÁLCULOS CORRETOS
    # =========================

    dias_passados = df_mes["data"].nunique()
    dias_restantes = metricas["dias_restantes"]

    # 🔥 total acumulado (ex: 25,69)
    total_acumulado = df_group["valor"].mean()

    # 🔥 média diária correta
    media = total_acumulado / dias_passados if dias_passados > 0 else 0

    # 🔥 projeção correta
    projecao = media * (dias_passados + dias_restantes)

    return {
        "df": df_group,
        "media": media,
        "projecao": projecao,
        "total_acumulado": total_acumulado
    }


# ============================================================
# ANALISE DIAS DA SEMANA
# ============================================================

def analise_dia_semana(dados, ano):

    df = dados["base_fat"].copy()
    df = df[df["ano"] == ano]

    df["dia_semana"] = df["data"].dt.day_name()

    dias_map = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    df["dia_semana"] = df["dia_semana"].map(dias_map)

    # 🔹 base diária (ESSENCIAL)
    df = (
        df
        .groupby(["dia_semana", df["data"].dt.date])
        .agg({
            "faturamento": "sum",
            "cupom": "sum"
        })
        .reset_index()
    )

    # 🔹 ticket médio correto
    df["ticket_medio"] = df.apply(
        lambda x: x["faturamento"] / x["cupom"] if x["cupom"] > 0 else 0,
        axis=1
    )

    # 🔹 agregação final
    df = (
        df
        .groupby("dia_semana")
        .agg({
            "faturamento": "mean",
            "ticket_medio": "mean",
            "cupom": "mean"
        })
        .reset_index()
    )

    ordem = [
        "Segunda-feira", "Terça-feira", "Quarta-feira",
        "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
    ]

    df["dia_semana"] = pd.Categorical(df["dia_semana"], categories=ordem, ordered=True)

    df = df.sort_values("dia_semana")

    df.rename(columns={
        "faturamento": "faturamento_medio",
        "ticket_medio": "ticket_medio",
        "cupom": "media_cupons"
    }, inplace=True)

    df["faturamento_medio"] = df["faturamento_medio"].round(0).astype(int)
    df["ticket_medio"] = df["ticket_medio"].round(0).astype(int)
    df["media_cupons"] = df["media_cupons"].round(0).astype(int)

    return df


# ============================================================
# ANALISE COMISSAO POR DIA COLABORADOR
# ============================================================
def comissao_por_dia_colaborador(dados, ano, mes):

    df = dados["base_comissao"].copy()
    df_colab = dados["base_colaboradores"].copy()

    if df.empty:
        return df

    # =========================
    # FILTRO
    # =========================
    df = df[
        (df["ano"] == ano) &
        (df["mes"] == mes)
    ]

    # =========================
    # TOTAL DO DIA (ANTES DO RATEIO)
    # =========================
    total_dia = (
        df
        .groupby("data")["valor"]
        .sum()
        .rename("Comissao_dia")
    )

    # =========================
    # JOIN COM COLABORADORES
    # =========================
    df = df.merge(
        df_colab,
        left_on="colaborador_id",
        right_on="id",
        how="left"
    )

    df = df.rename(columns={"nome": "colaborador"})

    # =========================
    # AGRUPAMENTO
    # =========================
    df_group = (
        df
        .groupby(["data", "colaborador"])["valor"]
        .sum()
        .reset_index()
    )

    # =========================
    # PIVOT
    # =========================
    df_pivot = df_group.pivot(
        index="data",
        columns="colaborador",
        values="valor"
    ).fillna(0)

    # =========================
    # ADICIONAR COLUNA TOTAL DIA
    # =========================
    df_pivot = df_pivot.merge(
        total_dia,
        left_index=True,
        right_index=True
    )

    # 🔥 COLOCAR COMO SEGUNDA COLUNA
    cols = df_pivot.columns.tolist()
    cols.insert(0, cols.pop(cols.index("Comissao_dia")))
    df_pivot = df_pivot[cols]

    # =========================
    # FORMATAR DATA
    # =========================
    df_pivot.index = df_pivot.index.strftime("%Y-%m-%d")

    # =========================
    # ORDENAR
    # =========================
    df_pivot = df_pivot.sort_index()

    return df_pivot


# ============================================================
# ANALISE RESUMO FATURAMENTO
# ============================================================
def resumo_faturamento(df_base):

    if df_base.empty:
        return 0, 0, 0

    # =========================
    # AGRUPAR POR DIA
    # =========================
    df_dia = (
        df_base
        .groupby("data")
        .agg({
            "faturamento": "sum",
            "cupom": "sum"
        })
        .reset_index()
    )

    # =========================
    # 🔥 CONSIDERAR APENAS DIAS COM OPERAÇÃO
    # =========================
    df_dia = df_dia[df_dia["faturamento"] > 0]

    dias = len(df_dia)

    faturamento_total = df_dia["faturamento"].sum()
    cupons_total = df_dia["cupom"].sum()

    fat_medio = faturamento_total / dias if dias else 0
    ticket = faturamento_total / cupons_total if cupons_total else 0
    cupons_medio = cupons_total / dias if dias else 0

    return fat_medio, ticket, cupons_medio