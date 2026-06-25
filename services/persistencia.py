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
    Atualiza ou cria o registro da tabela comissao_dia.
    """

    cursor = conn.cursor()

    # ==========================================
    # TENTA ATUALIZAR
    # ==========================================

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

    # ==========================================
    # SE NÃO EXISTIR, INSERE
    # ==========================================

    if linhas_afetadas == 0:

        cursor.execute(
            """
            INSERT INTO comissao_dia (
                data,
                comiss_dia
            )
            VALUES (%s, %s)
            """,
            (
                data,
                comissao_dia["comiss_dia"],
            ),
        )

        linhas_afetadas = 1

    cursor.close()

    return linhas_afetadas


# ==========================================
# ATUALIZAR VENDA_PRODUTOS
# ==========================================

def salvar_produtos(
    conn,
    data: str,
    nome_arquivo: str,
    df_produtos,
):
    """
    Salva os produtos extraídos do relatório.
    """

    cursor = conn.cursor()

    linhas_afetadas = 0

    for _, row in df_produtos.iterrows():

        cursor.execute(
            """
            INSERT INTO venda_produtos (
                data,
                cod_produto,
                produto,
                qtd,
                valor_total,
                origem_arquivo
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (data, cod_produto)
            DO UPDATE SET
                produto = EXCLUDED.produto,
                qtd = EXCLUDED.qtd,
                valor_total = EXCLUDED.valor_total,
                origem_arquivo = EXCLUDED.origem_arquivo
            """,
            (
                data,
                row["cod_produto"],
                row["produto"],
                row["qtd"],
                row["valor_total"],
                nome_arquivo,
            ),
        )

        linhas_afetadas += 1

    cursor.close()

    return linhas_afetadas