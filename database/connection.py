#import sqlite3
#
#def get_connection():
#    """
#    Retorna conexão com o banco SQLite
#    """
#    caminho_banco = "faturamento_scada.db"
#    return sqlite3.connect(caminho_banco)


import psycopg2
import pandas as pd


def get_connection():
    return psycopg2.connect(
        "postgresql://postgres:C,9b4zYMyi6Wa?e@db.fdepgcrcngsgdsvxfjpi.supabase.co:5432/postgres"
    )


def carregar_dados():
    conn = get_connection()

    dados = {}

    try:
        dados["base_fat"] = pd.read_sql("SELECT * FROM base_fat", conn)
    except:
        dados["base_fat"] = pd.DataFrame()

    try:
        dados["base_perdas"] = pd.read_sql("SELECT * FROM perdas", conn)
    except:
        dados["base_perdas"] = pd.DataFrame()

    try:
        dados["base_produtos"] = pd.read_sql("SELECT * FROM venda_produtos", conn)
    except:
        dados["base_produtos"] = pd.DataFrame()

    try:
        dados["base_comissao"] = pd.read_sql("SELECT * FROM comissao_colaborador", conn)
    except:
        dados["base_comissao"] = pd.DataFrame()

    conn.close()

    return dados