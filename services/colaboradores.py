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

    nome = nome.strip()

    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se já existe colaborador com o mesmo nome
    cursor.execute("""
        SELECT 1
        FROM colaboradores
        WHERE LOWER(nome) = LOWER(%s)
    """, (nome,))

    if cursor.fetchone():

        conn.close()

        raise ValueError(
            "Já existe um colaborador com esse nome."
        )

    cursor.execute("""
        INSERT INTO colaboradores (
            nome,
            ativo
        )
        VALUES (%s, TRUE)
    """, (nome,))

    conn.commit()
    conn.close()


# ==========================================
# EDITAR COLABORADOR
# ==========================================

def editar_colaborador(colaborador_id, novo_nome):

    novo_nome = novo_nome.strip()

    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se existe outro colaborador com o mesmo nome
    cursor.execute("""
        SELECT 1
        FROM colaboradores
        WHERE LOWER(nome) = LOWER(%s)
          AND id <> %s
    """, (novo_nome, colaborador_id))

    if cursor.fetchone():

        conn.close()

        raise ValueError(
            "Já existe um colaborador com esse nome."
        )

    cursor.execute("""
        UPDATE colaboradores
        SET nome = %s
        WHERE id = %s
    """, (novo_nome, colaborador_id))

    conn.commit()
    conn.close()


# ==========================================
# LISTA COLABORADOR
# ==========================================

def listar_colaboradores_select(ativo=True):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome
        FROM colaboradores
        WHERE ativo = %s
        ORDER BY nome
    """, (ativo,))

    colaboradores = cursor.fetchall()

    conn.close()

    return colaboradores


# ==========================================
# ALTERAR STATUS DO COLABORADOR
# ==========================================

def alterar_status_colaborador(colaborador_id, ativo):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE colaboradores
        SET ativo = %s
        WHERE id = %s
    """, (ativo, colaborador_id))

    if cursor.rowcount == 0:

        conn.close()

        raise ValueError(
            "Colaborador não encontrado."
        )

    conn.commit()
    conn.close()