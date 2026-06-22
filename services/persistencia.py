# ==========================================
# CONEXÃO COM O BANCO
# ==========================================

from database.connection import get_connection

# ==========================================
# ATUALIZAR BASE_FAT
# ==========================================

def salvar_base_fat(conn, data: str, base_fat: dict):
    """
    Atualiza os dados da tabela base_fat.
    """

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE base_fat
        SET
            faturamento = %s,
            cupom = %s,
            ticket_medio = %s
        WHERE data = %s
        """,
        (
            base_fat["faturamento"],
            base_fat["cupom"],
            base_fat["ticket_medio"],
            data,
        ),
    )

    linhas_afetadas = cursor.rowcount

    cursor.close()

    return linhas_afetadas