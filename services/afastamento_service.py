import calendar

from datetime import (
    timedelta,
    date,
)
from database.connection import get_connection
from services.comissao_service import (
    existe_comissao_dia,
    atualizar_presenca,
    recalcular_comissao_dia,
    listar_colaboradores_ativos
)


# ==========================================================
# Status do calendário de participação
# ==========================================================

STATUS_PRESENTE = "✔"

STATUS_FERIAS = "Férias"

STATUS_ATESTADO = "Atestado"

STATUS_LICENCA = "Licensa"

STATUS_FOLGA = "Folga"

STATUS_FALTA = "Falta"

STATUS_OUTRO = "Outro"

STATUS_AFASTADO = "Afastamento"


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

    datas = listar_datas_periodo(
        afastamento["data_inicio"],
        afastamento["data_fim"],
    )

    for data in datas:

        if existe_comissao_dia(data):

            atualizar_presenca(
                data,
                afastamento["colaborador_id"],
                False,
            )

            recalcular_comissao_dia(data)

    return True


# ==========================================================
# Excluir afastamento
# ==========================================================

def excluir_afastamento(
    afastamento_id,
):
    """
    Exclui um afastamento programado.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM afastamentos_programados
        WHERE id = %s
        """,
        (
            afastamento_id,
        ),
    )

    conn.commit()

    cursor.close()
    conn.close()


def listar_datas_periodo(data_inicio, data_fim):
    """
    Retorna todas as datas compreendidas no período.
    """

    datas = []

    data = data_inicio

    while data <= data_fim:

        datas.append(data)

        data += timedelta(days=1)

    return datas


def listar_afastamentos_mes(
    ano,
    mes,
):
    """
    Retorna todos os afastamentos ativos que
    possuem interseção com o mês informado.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            colaborador_id,
            data_inicio,
            data_fim,
            motivo
        FROM
            afastamentos_programados
        WHERE
            ativo = TRUE
            AND data_inicio <= %s
            AND data_fim >= %s
        ORDER BY
            colaborador_id,
            data_inicio
        """,
        (
            date(
                ano,
                mes,
                calendar.monthrange(
                    ano,
                    mes,
                )[1]
            ),
            date(
                ano,
                mes,
                1,
            ),
        ),
    )

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "colaborador_id": linha[0],
            "data_inicio": linha[1],
            "data_fim": linha[2],
            "motivo": linha[3],
        }
        for linha in resultados
    ]


# ==========================================================
# Afastamentos de uma data
# ==========================================================

def listar_afastamentos_data(
    data,
):
    """
    Retorna todos os afastamentos ativos
    para uma data específica.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            colaborador_id,
            motivo
        FROM
            afastamentos_programados
        WHERE
            ativo = TRUE
            AND data_inicio <= %s
            AND data_fim >= %s
        ORDER BY
            colaborador_id
        """,
        (
            data,
            data,
        ),
    )

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "colaborador_id": linha[0],
            "motivo": linha[1],
        }
        for linha in resultados
    ]


# ==========================================================
# Aplicação automática de afastamentos
# ==========================================================

def aplicar_afastamentos_importacao(
    conn,
    data,
):
    """
    Aplica automaticamente os afastamentos
    programados durante a importação do relatório.
    """

    afastamentos = listar_afastamentos_data(
        data,
    )

    if not afastamentos:
        return

    cursor = conn.cursor()

    for afastamento in afastamentos:

        cursor.execute(
            """
            UPDATE comissao_colaborador
            SET
                presente = FALSE
            WHERE
                data = %s
                AND colaborador_id = %s
            """,
            (
                data,
                afastamento["colaborador_id"],
            ),
        )

    cursor.close()



def listar_faltas_mes(
    ano,
    mes,
):
    """
    Retorna todas as faltas registradas
    na comissão do mês.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            colaborador_id,
            data
        FROM
            comissao_colaborador
        WHERE
            presente = FALSE
            AND EXTRACT(YEAR FROM data) = %s
            AND EXTRACT(MONTH FROM data) = %s
        ORDER BY
            data,
            colaborador_id
        """,
        (
            ano,
            mes,
        ),
    )

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "colaborador_id": linha[0],
            "data": linha[1],
        }
        for linha in resultados
    ]



def obter_calendario_mensal(
    ano,
    mes,
):
    """
    Monta o calendário mensal de participação dos colaboradores.
    """

    colaboradores = listar_colaboradores_ativos()

    afastamentos = listar_afastamentos_mes(
        ano,
        mes,
    )

    faltas = listar_faltas_mes(
        ano,
        mes,
    )


    indice_afastamentos = {}

    for afastamento in afastamentos:

        data = afastamento["data_inicio"]

        while data <= afastamento["data_fim"]:

            indice_afastamentos[
                (
                    afastamento["colaborador_id"],
                    data,
                )
            ] = afastamento["motivo"]

            data += timedelta(days=1)

    dias_mes = calendar.monthrange(
        ano,
        mes,
    )[1]


    indice_faltas = {}

    for falta in faltas:

        indice_faltas[
            (
                falta["colaborador_id"],
                falta["data"],
            )
        ] = STATUS_FALTA

    calendario = []

    for dia in range(1, dias_mes + 1):

        data_atual = date(
            ano,
            mes,
            dia,
        )

        dias_semana = [
            "Seg",
            "Ter",
            "Qua",
            "Qui",
            "Sex",
            "Sáb",
            "Dom",
        ]

        linha = {
            "Data": (
                f"{data_atual.strftime('%d/%m')} "
                f"({dias_semana[data_atual.weekday()]})"
            )
        }

        for colaborador in colaboradores:

            chave = (
                colaborador["id"],
                data_atual,
            )

            motivo = indice_afastamentos.get(chave)

            if motivo is not None:

                if motivo == "Férias":
                    status = STATUS_FERIAS

                elif motivo == "Atestado":
                    status = STATUS_ATESTADO

                elif motivo == "Licença":
                    status = STATUS_LICENCA

                elif motivo == "Folga":
                    status = STATUS_FOLGA

                else:
                    status = STATUS_OUTRO

            else:

                status = indice_faltas.get(
                    chave,
                    STATUS_PRESENTE,
                )

            linha[colaborador["nome"]] = status

        calendario.append(linha)

    return calendario


