import pandas as pd

from database.connection import get_connection


# ==========================================
# LISTAR COLABORADORES
# ==========================================

def listar_colaboradores():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            ativo
        FROM colaboradores
        ORDER BY nome
    """)

    colaboradores = cursor.fetchall()

    conn.close()

    df = pd.DataFrame(
        colaboradores,
        columns=[
            "ID",
            "Nome",
            "Ativo"
        ]
    )

    df["Status"] = df["Ativo"].map({
        True: "🟢 Ativo",
        False: "🔴 Inativo"
    })

    df = df.drop(columns=["Ativo"])

    return df


# ==========================================
# ADICIONAR COLABORADOR
# ==========================================

def adicionar_colaborador(nome):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO colaboradores (
            nome,
            ativo
        )
        VALUES (%s, TRUE)
    """, (nome.strip(),))

    conn.commit()
    conn.close()