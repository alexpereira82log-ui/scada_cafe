from database.connection import get_connection


# ==========================================
# CONSULTAR FATURAMENTO
# ==========================================

def consultar_faturamento(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            data,
            faturamento,
            meta,
            cupom,
            ticket_medio
        FROM base_fat
        WHERE data = %s
    """, (data,))

    registro = cursor.fetchone()

    conn.close()

    if registro is None:

        raise ValueError(
            "Data não encontrada."
        )

    return {
        "data": registro[0],
        "faturamento": registro[1],
        "meta": registro[2],
        "cupom": registro[3],
        "ticket_medio": registro[4],
    }


# ==========================================
# EDITAR FATURAMENTO
# ==========================================

def editar_faturamento(
    data,
    faturamento,
    meta,
    cupom,
    ticket_medio
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE base_fat
        SET
            faturamento = %s,
            meta = %s,
            cupom = %s,
            ticket_medio = %s
        WHERE data = %s
    """, (
        faturamento,
        meta,
        cupom,
        ticket_medio,
        data
    ))

    if cursor.rowcount == 0:

        conn.close()

        raise ValueError(
            "Data não encontrada."
        )

    conn.commit()
    conn.close()