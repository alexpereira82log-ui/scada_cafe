from datetime import date
from database.connection import get_connection

from services.comissao_service import (
    listar_colaboradores_ativos,
)



def obter_comissao_mes(
    ano,
    mes,
):
    """
    Retorna as comissões do mês indexadas pela data.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            data,
            comiss_dia
        FROM
            comissao_dia
        WHERE
            EXTRACT(YEAR FROM data) = %s
            AND EXTRACT(MONTH FROM data) = %s
        ORDER BY
            data
        """,
        (
            ano,
            mes,
        ),
    )

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        linha[0]: {
            "taxa_servico": float(linha[1] or 0),
            "comissao": float(linha[1] or 0) * 0.80,
        }
        for linha in resultados
    }



def obter_relatorio_mensal_comissao(
    ano,
    mes,
):
    """
    Retorna os dados do relatório gerencial
    da comissão do mês informado.
    """

    comissoes_dia = obter_comissao_mes(
        ano,
        mes,
    )

    comissoes_colaboradores = obter_comissoes_colaboradores_mes(
        ano,
        mes,
    )

    colaboradores = listar_colaboradores_ativos()

    # ==========================================================
    # Índice das comissões individuais
    # ==========================================================

    indice_comissoes = {}

    for registro in comissoes_colaboradores:

        data = registro[0]
        colaborador = registro[1]
        valor = float(
            registro[2] or 0
        )

        indice_comissoes[
            (
                data,
                colaborador,
            )
        ] = valor

    # ==========================================================
    # Montagem do relatório
    # ==========================================================

    relatorio = []

    for data, valores in comissoes_dia.items():

        linha = {
            "Data": data,
            "Taxa Serviço": valores["taxa_servico"],
            "Comissão (80%)": valores["comissao"],
        }

    
        # ==========================================================
        # Comissão individual dos colaboradores
        # ==========================================================

        for colaborador in colaboradores:

            linha[colaborador["nome"]] = indice_comissoes.get(
                (
                    data,
                    colaborador["nome"],
                ),
                0,
            )

        relatorio.append(
            linha
        )

    return relatorio


def obter_comissoes_colaboradores_mes(
    ano,
    mes,
):
    """
    Retorna todas as comissões individuais
    do mês.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cc.data,
            c.nome,
            cc.valor,
            cc.presente

        FROM
            comissao_colaborador cc

        INNER JOIN colaboradores c
            ON c.id = cc.colaborador_id

        WHERE
            EXTRACT(YEAR FROM cc.data) = %s
            AND EXTRACT(MONTH FROM cc.data) = %s

        ORDER BY
            cc.data,
            c.nome
        """,
        (
            ano,
            mes,
        ),
    )

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultados