from database.connection import get_connection


# ==========================================
# INSERIR PERDA
# ==========================================

def inserir_perda(
    data,
    item,
    categoria,
    qtd,
    motivo,
    responsavel,
    obs
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO perdas (
                data,
                item,
                categoria,
                qtd,
                motivo,
                responsavel,
                obs
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data,
            item,
            categoria,
            qtd,
            motivo,
            responsavel,
            obs
        ))

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()

# ==========================================
# CONSULTAR PERDAS
# ==========================================

def consultar_perdas(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            data,
            item,
            categoria,
            qtd,
            motivo,
            responsavel,
            obs
        FROM perdas
        WHERE data = %s
        ORDER BY id
    """, (data,))

    colunas = [desc[0] for desc in cursor.description]

    registros = [
        dict(zip(colunas, linha))
        for linha in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return registros

# ==========================================
# CONSULTAR UMA PERDA
# ==========================================

def consultar_perda(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            data,
            item,
            categoria,
            qtd,
            motivo,
            responsavel,
            obs
        FROM perdas
        WHERE id = %s
    """, (id,))

    registro = cursor.fetchone()

    cursor.close()
    conn.close()

    if registro is None:

        raise ValueError(
            "Registro não encontrado."
        )

    colunas = [
        "id",
        "data",
        "item",
        "categoria",
        "qtd",
        "motivo",
        "responsavel",
        "obs"
    ]

    return dict(zip(colunas, registro))

# ==========================================
# EDITAR PERDA
# ==========================================

def editar_perda(
    id,
    data,
    item,
    categoria,
    qtd,
    motivo,
    responsavel,
    obs
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE perdas
            SET
                data = %s,
                item = %s,
                categoria = %s,
                qtd = %s,
                motivo = %s,
                responsavel = %s,
                obs = %s
            WHERE id = %s
        """, (
            data,
            item,
            categoria,
            qtd,
            motivo,
            responsavel,
            obs,
            id
        ))

        if cursor.rowcount == 0:

            raise ValueError(
                "Registro não encontrado."
            )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()

# ==========================================
# EXCLUIR PERDA
# ==========================================

def excluir_perda(id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM perdas
            WHERE id = %s
        """, (id,))

        if cursor.rowcount == 0:

            raise ValueError(
                "Registro não encontrado."
            )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()

# ==========================================
# EXCLUIR PERDA
# ==========================================

def excluir_perda(id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM perdas
            WHERE id = %s
        """, (id,))

        if cursor.rowcount == 0:

            raise ValueError(
                "Registro não encontrado."
            )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()

# ==========================================
# CARREGAR COLABORADORES
# ==========================================

def carregar_colaboradores():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome
        FROM colaboradores
        WHERE ativo = TRUE
        ORDER BY nome
    """)

    colaboradores = [
        row[0]
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return colaboradores

