import sqlite3

DB_PATH = "faturamento_scada.db"


def get_connection():
    """
    Retorna uma conexão com o banco SQLite.
    """
    return sqlite3.connect(DB_PATH)