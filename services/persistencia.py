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

# ==========================================
# ATUALIZAR COMISSAO_DIA
# ==========================================

def salvar_comissao_dia(conn, data: str, comissao_dia: dict):
    """
    Atualiza os dados da tabela comissao_dia.
    """

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE comissao_dia
        SET
            comiss_dia = %s
        WHERE data = %s
        """,
        (
            comissao_dia["comiss_dia"],
            data,
        ),
    )

    linhas_afetadas = cursor.rowcount

    cursor.close()

    return linhas_afetadas