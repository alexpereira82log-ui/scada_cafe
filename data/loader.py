import pandas as pd
from database.connection import get_connection


def carregar_tabela(conn, nome_tabela):
    """
    Carrega uma tabela do banco de forma segura.
    """
    try:
        df = pd.read_sql(f"SELECT * FROM {nome_tabela}", conn)
        print(f"✅ Tabela '{nome_tabela}' carregada ({len(df)} registros)")
        return df

    except Exception as e:
        print(f"⚠️ Erro ao carregar tabela '{nome_tabela}': {e}")
        return pd.DataFrame()


def carregar_dados():
    """
    Carrega todas as tabelas do banco e retorna um dicionário de DataFrames.
    """

    tabelas = {
        "base_fat": "base_fat",
        "base_comissao": "comissao_colaborador",
        "base_perdas": "perdas",
        "base_produtos": "venda_produtos",
        "base_colaboradores": "colaboradores",
    }

    dados = {}

    # 🔥 conexão segura
    with get_connection() as conn:

        for chave, tabela in tabelas.items():
            dados[chave] = carregar_tabela(conn, tabela)

    # 🔥 GARANTIA DE CHAVES (EVITA KeyError)
    for chave in tabelas.keys():
        if chave not in dados:
            dados[chave] = pd.DataFrame()

    # 🔍 DEBUG FINAL
    print("\n📦 DADOS CARREGADOS:")
    for chave, df in dados.items():
        print(f"{chave}: {df.shape}")

    return dados