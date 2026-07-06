from database.connection import get_connection


def obter_comissao_dia(data):
    """
    Retorna o registro da comissão de um determinado dia.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT data, comiss_dia
        FROM comissao_dia
        WHERE data = %s
        """,
        (data,)
    )

    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    if resultado is None:
        return None

    return {
        "data": resultado[0],
        "valor_taxa_servico": resultado[1]
    }


def listar_rateio_dia(data):
    """
    Retorna os colaboradores e suas informações de comissão
    para uma determinada data.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cc.colaborador_id,
            c.nome,
            c.ativo,
            cc.presente,
            cc.valor
        FROM comissao_colaborador cc
        INNER JOIN colaboradores c
            ON c.id = cc.colaborador_id
        WHERE cc.data = %s
        ORDER BY c.nome
        """,
        (data,)
    )

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": linha[0],
            "nome": linha[1],
            "ativo": linha[2],
            "presente": linha[3],
            "valor": float(linha[4] or 0),
        }
        for linha in resultados
    ]


def recalcular_rateio(participantes, valor_rateio):
    """
    Recalcula a comissão dos colaboradores elegíveis.
    """

    elegiveis = sum(
        participante["Participa"]
        for participante in participantes
    )

    if elegiveis > 0:
        valor_individual = valor_rateio / elegiveis
    else:
        valor_individual = 0


    for participante in participantes:

        if participante["Participa"]:
            participante["Comissão"] = round(
                valor_individual,
                2
            )

        else:
            participante["Comissão"] = 0

    return participantes, elegiveis, valor_individual


def salvar_rateio(data, participantes):
    """
    Atualiza o rateio da comissão dos colaboradores.
    """
    
    conn = get_connection()
    cursor = conn.cursor()

    for participante in participantes:

        cursor.execute(
            """
            UPDATE comissao_colaborador
            SET
                presente = %s,
                valor = %s
            WHERE
                data = %s
                AND colaborador_id = %s
            """,
            (
                participante["Participa"],
                participante["Comissão"],
                data,
                participante["ID"],
            ),
        )

    conn.commit()

    cursor.close()
    conn.close()



def listar_colaboradores_ativos():
    """
    Retorna todos os colaboradores ativos ordenados pelo nome.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, nome
        FROM colaboradores
        WHERE ativo = TRUE
        ORDER BY nome
        """
    )

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": linha[0],
            "nome": linha[1],
        }
        for linha in resultados
    ]