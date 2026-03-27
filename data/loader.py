import pandas as pd
from database.connection import get_connection


def carregar_dados():
    """
    Carrega todas as tabelas do banco e retorna um dicionário de DataFrames.
    """

    with get_connection() as conn:
        dados = {
            "base_fat": pd.read_sql("SELECT * FROM base_fat", conn),
            "base_comissao": pd.read_sql("SELECT * FROM comissao_colaborador", conn),
            "base_perdas": pd.read_sql("SELECT * FROM perdas", conn),
            "base_produtos": pd.read_sql("SELECT * FROM venda_produtos", conn),
        }

    return dados