import sqlite3

def get_connection():
    """
    Retorna conexão com o banco SQLite
    """
    caminho_banco = "faturamento_scada.db"
    return sqlite3.connect(caminho_banco)

