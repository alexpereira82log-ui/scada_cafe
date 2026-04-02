import pandas as pd
import locale


def tratar_dados(dados: dict) -> dict:
    """
    Recebe o dicionário de DataFrames e aplica todos os tratamentos necessários.
    """

    base_fat_df = dados["base_fat"]
    base_comissao_df = dados["base_comissao"]
    base_perdas_df = dados["base_perdas"]
    base_produtos_df = dados["base_produtos"]

    # =========================
    # TRATAMENTO BASE FATURAMENTO
    # =========================
    base_fat_df["meta"] = pd.to_numeric(base_fat_df["meta"], errors="coerce")
    base_fat_df["faturamento"] = pd.to_numeric(base_fat_df["faturamento"], errors="coerce")
    base_fat_df["data"] = pd.to_datetime(base_fat_df["data"], errors="coerce")

    base_fat_df["ano"] = base_fat_df["data"].dt.year
    base_fat_df["mes"] = base_fat_df["data"].dt.month

    # =========================
    # TRATAMENTO COMISSÃO
    # =========================
    base_comissao_df["data"] = pd.to_datetime(base_comissao_df["data"], errors="coerce")

    base_comissao_df["ano"] = base_comissao_df["data"].dt.year
    base_comissao_df["mes"] = base_comissao_df["data"].dt.month

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

    # Garantir data
    base_produtos_df["data"] = pd.to_datetime(base_produtos_df["data"], errors="coerce")

    # Criar mes e ano corretamente (AQUI ESTAVA O ERRO)
    base_produtos_df["mes"] = base_produtos_df["data"].dt.month
    base_produtos_df["ano"] = base_produtos_df["data"].dt.year

    # =========================
    # TRATAMENTO PERDAS
    # =========================
    base_perdas_df["data"] = pd.to_datetime(base_perdas_df["data"], errors="coerce")

    base_perdas_df["qtd"] = (
        base_perdas_df["qtd"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.extract(r"(\d+\.?\d*)")[0]
    )

    base_perdas_df["qtd"] = pd.to_numeric(base_perdas_df["qtd"], errors="coerce")

    # =========================
    # LOCALE (meses em PT-BR)
    # =========================
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    except:
        pass

    base_fat_df["mes_nome"] = base_fat_df["data"].dt.strftime("%B").str.capitalize()

    # =========================
    # RETORNO
    # =========================
    return {
        "base_fat": base_fat_df,
        "base_comissao": base_comissao_df,
        "base_perdas": base_perdas_df,
        "base_produtos": base_produtos_df,
    }