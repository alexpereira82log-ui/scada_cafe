import sqlite3
import pandas as pd


def carregar_dados():
    """
    Carrega todas as tabelas do banco SQLite e retorna em um dicionário.
    """

    caminho_banco = "faturamento_scada.db"

    with sqlite3.connect(caminho_banco) as conn:
        base_fat = pd.read_sql("SELECT * FROM base_fat", conn)
        base_comissao = pd.read_sql("SELECT * FROM comissao_colaborador", conn)
        base_perdas = pd.read_sql("SELECT * FROM perdas", conn)
        base_produtos = pd.read_sql("SELECT * FROM venda_produtos", conn)

    return {
        "base_fat": base_fat,
        "base_comissao": base_comissao,
        "base_perdas": base_perdas,
        "base_produtos": base_produtos,
    }