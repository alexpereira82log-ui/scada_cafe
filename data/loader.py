import pandas as pd
from database.connection import get_connection


def carregar_dados():
    """
    Carrega todas as tabelas do banco e retorna um dicionário de DataFrames.
    """

    conn = get_connection()

    dados = {}

    try:
        dados["base_fat"] = pd.read_sql("SELECT * FROM base_fat", conn)
    except:
        dados["base_fat"] = pd.DataFrame()

    try:
        dados["base_comissao"] = pd.read_sql("SELECT * FROM comissao_colaborador", conn)
    except:
        dados["base_comissao"] = pd.DataFrame()

    try:
        dados["base_perdas"] = pd.read_sql("SELECT * FROM perdas", conn)
    except:
        dados["base_perdas"] = pd.DataFrame()

    try:
        dados["base_produtos"] = pd.read_sql("SELECT * FROM venda_produtos", conn)
    except:
        dados["base_produtos"] = pd.DataFrame()

    conn.close()

    return dados