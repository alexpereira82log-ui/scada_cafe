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