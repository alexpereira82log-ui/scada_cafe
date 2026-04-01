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

    resultado = df_mes[["data", "faturamento"]].dropna()

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
    df = dados["base_perdas"]

    df_filtrado = df[
        (df["data"].dt.year == ano) &
        (df["data"].dt.month == mes)
    ]

    resultado = (
        df_filtrado
        .groupby("motivo")[["item"]]
        .count()
        .reset_index()
        .sort_values("item", ascending=False)
    )

    return resultado


# ============================================================
# PERDAS POR MÊS
# ============================================================
def perdas_por_mes(dados: dict, ano: int) -> pd.DataFrame:
    df = dados["base_perdas"].copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    df_ano = df[df["data"].dt.year == ano]

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

    df = dados["base_comissao"].copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # Filtrar mês
    df_mes = df[
        (df["data"].dt.year == ano) &
        (df["data"].dt.month == mes)
    ]

    # ❌ Remover Brunna
    df_mes = df_mes[df_mes["colaborador_id"] != 1]

    if df_mes.empty:
        return {
            "df": pd.DataFrame(),
            "media": 0,
            "projecao": 0
        }

    # Agrupar comissão
    df_group = (
        df_mes
        .groupby("colaborador_id")["valor"]
        .sum()
        .reset_index()
    )

    # 🔥 BUSCAR NOMES DIRETO DO BANCO (SOLUÇÃO ROBUSTA)
    conn = get_connection()
    df_colab = pd.read_sql("SELECT id, nome FROM colaboradores", conn)
    conn.close()

    # Merge
    df_group = df_group.merge(
        df_colab,
        left_on="colaborador_id",
        right_on="id",
        how="left"
    )

    df_group = df_group.sort_values("valor", ascending=False)

    df_group = df_group[["nome", "valor"]]

    # Média
    media = df_group["valor"].mean()

    # Dias
    dias_passados = df_mes["data"].nunique()
    dias_restantes = metricas["dias_restantes"]

    projecao = media * (dias_passados + dias_restantes) if dias_passados > 0 else 0

    return {
        "df": df_group,
        "media": media,
        "projecao": projecao
    }