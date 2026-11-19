import os
import streamlit as st
import psycopg2


def obter_senha():
    """
    Obtém a senha do banco conforme o ambiente.
    """

    try:
        senha = st.secrets["SUPABASE_DB_PASSWORD"]
    except Exception:
        senha = os.getenv("SUPABASE_DB_PASSWORD")

    if not senha:
        raise RuntimeError(
            "Senha do banco não encontrada nas configurações."
        )

    return senha


def get_connection():
    return psycopg2.connect(
        host="aws-0-us-west-2.pooler.supabase.com",
        database="postgres",
        user="postgres.fdepgcrcngsgdsvxfjpi",
        password=obter_senha(),
        port=6543,
        sslmode="require"
    )
