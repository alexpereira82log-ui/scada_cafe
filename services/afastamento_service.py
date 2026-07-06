from database.connection import get_connection


def registrar_afastamento(afastamento):
    """
    Registra um afastamento programado.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO afastamentos_programados
        (
            colaborador_id,
            data_inicio,
            data_fim,
            motivo,
            observacao
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            afastamento["colaborador_id"],
            afastamento["data_inicio"],
            afastamento["data_fim"],
            afastamento["motivo"],
            afastamento["observacao"],
        ),
    )

    conn.commit()

    cursor.close()
    conn.close()


def listar_afastamentos():
    """
    Retorna todos os afastamentos ativos.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            ap.id,
            c.nome,
            ap.data_inicio,
            ap.data_fim,
            ap.motivo,
            ap.observacao
        FROM afastamentos_programados ap
        INNER JOIN colaboradores c
            ON c.id = ap.colaborador_id
        WHERE ap.ativo = TRUE
        ORDER BY
            ap.data_inicio DESC,
            c.nome
        """
    )

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": linha[0],
            "colaborador": linha[1],
            "data_inicio": linha[2],
            "data_fim": linha[3],
            "motivo": linha[4],
            "observacao": linha[5],
        }
        for linha in resultados
    ]


def aplicar_afastamento(afastamento):
    """
    Aplica um afastamento programado.
    """

    registrar_afastamento(afastamento)

    return True