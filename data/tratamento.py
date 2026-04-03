import pandas as pd
import locale


def tratar_dados(dados: dict) -> dict:
    """
    Recebe um dicionário de DataFrames e retorna os dados tratados.
    """

    base_fat_df = dados["base_fat"]
    base_comissao_df = dados["base_comissao"]
    base_perdas_df = dados["base_perdas"]
    base_produtos_df = dados["base_produtos"]

    # ============================================================
    # CONFIGURAÇÃO DE LOCALE (MESES EM PORTUGUÊS)
    # ============================================================
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    except:
        pass  # Evita erro em sistemas que não suportam locale

    # =========================
    # TRATAMENTO PRODUTOS
    # =========================
    colunas_numericas = ["qtd", "valor_unit", "valor_total", "perc_total_venda", "mtc"]

    for col in colunas_numericas:
        if col in base_produtos_df.columns:
            base_produtos_df[col] = (
                base_produtos_df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.replace("%", "", regex=False)
            )
            base_produtos_df[col] = pd.to_numeric(base_produtos_df[col], errors="coerce")

    # 🔥 ESSA É A BASE CORRETA AGORA
    base_produtos_df["data"] = pd.to_datetime(base_produtos_df["data"], errors="coerce")

    base_produtos_df["mes"] = base_produtos_df["data"].dt.month
    base_produtos_df["ano"] = base_produtos_df["data"].dt.year

    # ============================================================
    # TRATAMENTO BASE FATURAMENTO
    # ============================================================
    base_fat_df["meta"] = pd.to_numeric(base_fat_df["meta"], errors="coerce")
    base_fat_df["faturamento"] = pd.to_numeric(base_fat_df["faturamento"], errors="coerce")
    base_fat_df["data"] = pd.to_datetime(base_fat_df["data"])

    base_fat_df["ano"] = base_fat_df["data"].dt.year
    base_fat_df["mes"] = base_fat_df["data"].dt.month
    base_fat_df["mes_nome"] = base_fat_df["data"].dt.strftime("%B").str.capitalize()

    # ============================================================
    # TRATAMENTO BASE COMISSÃO
    # ============================================================
    base_comissao_df["data"] = pd.to_datetime(base_comissao_df["data"])

    base_comissao_df["ano"] = base_comissao_df["data"].dt.year
    base_comissao_df["mes"] = base_comissao_df["data"].dt.month
    base_comissao_df["mes_nome"] = base_comissao_df["data"].dt.strftime("%B").str.capitalize()

    # ============================================================
    # TRATAMENTO BASE PERDAS
    # ============================================================
    base_perdas_df["data"] = pd.to_datetime(base_perdas_df["data"])

    base_perdas_df["qtd"] = (
        base_perdas_df["qtd"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.extract(r"(\d+\.?\d*)")[0]
    )

    base_perdas_df["qtd"] = pd.to_numeric(base_perdas_df["qtd"], errors="coerce")

    # ============================================================
    # RETORNO PADRONIZADO
    # ============================================================
    return {
        "base_fat": base_fat_df,
        "base_comissao": base_comissao_df,
        "base_perdas": base_perdas_df,
        "base_produtos": base_produtos_df,
    }