import calendar

from database.connection import get_connection
from datetime import date




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
        participante["presente"]
        for participante in participantes
    )

    if elegiveis > 0:
        valor_individual = valor_rateio / elegiveis
    else:
        valor_individual = 0

    for participante in participantes:

        if participante["presente"]:
            participante["valor"] = round(
                valor_individual,
                2
            )
        else:
            participante["valor"] = 0

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
                participante["presente"],
                participante["valor"],
                data,
                participante["id"],
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



def recalcular_comissao_dia(data):
    """
    Recalcula toda a comissão de uma determinada data.

    Fluxo:
        1. Obtém a comissão do dia.
        2. Obtém os participantes.
        3. Recalcula o rateio.
        4. Salva os novos valores.

    Esta função será reutilizada por:
        - Gestão de Comissão
        - Afastamentos Programados
        - Importador de Fechamento
        - Futuras rotinas administrativas
    """

    # ==========================================================
    # Buscar comissão do dia
    # ==========================================================

    comissao = obter_comissao_dia(data)

    if comissao is None:
        return False
    
    # ==========================================================
    # Buscar participantes do dia
    # ==========================================================

    participantes = listar_rateio_dia(data)

    if not participantes:
        return False
    
    # ==========================================================
    # Calcular valor do rateio
    # ==========================================================

    valor_taxa = float(
        comissao["valor_taxa_servico"] or 0
    )

    valor_rateio = valor_taxa * 0.80

    # ==========================================================
    # Recalcular rateio
    # ==========================================================

    participantes, elegiveis, valor_individual = recalcular_rateio(
        participantes,
        valor_rateio,
    )

    # ==========================================================
    # Salvar novo rateio
    # ==========================================================

    salvar_rateio(
        data,
        participantes,
    )

    return True


def existe_comissao_dia(data):
    """
    Verifica se existe comissão cadastrada para uma data.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM comissao_dia
        WHERE data = %s
        """,
        (data,)
    )

    existe = cursor.fetchone() is not None

    cursor.close()
    conn.close()

    return existe


def atualizar_presenca(
    data,
    colaborador_id,
    presente,
):
    """
    Atualiza a presença de um colaborador em uma data.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE comissao_colaborador
        SET presente = %s
        WHERE
            data = %s
            AND colaborador_id = %s
        """,
        (
            presente,
            data,
            colaborador_id,
        ),
    )

    conn.commit()

    cursor.close()
    conn.close()



def obter_resumo_mensal_comissao(
    ano,
    mes,
):
    """
    Retorna os indicadores gerenciais da comissão
    para o mês informado.

    Indicadores:
    - Taxa de Serviço
    - Comissão Total (80%)
    - Média Diária
    - Média Individual
    - Projeção Individual (considerando presença integral)
    """

    conn = get_connection()
    cursor = conn.cursor()

    # ==========================================================
    # Taxa de serviço e dias com comissão
    # ==========================================================

    cursor.execute(
        """
        SELECT
            COALESCE(
                SUM(comiss_dia),
                0
            ) AS taxa_servico,

            COUNT(*) AS dias_comissao

        FROM comissao_dia

        WHERE
            EXTRACT(YEAR FROM data) = %s
            AND EXTRACT(MONTH FROM data) = %s
        """,
        (
            ano,
            mes,
        ),
    )

    resultado = cursor.fetchone()

    taxa_servico = float(resultado[0])
    dias_comissao = resultado[1]


    # ==========================================================
    # Média individual
    # ==========================================================

    cursor.execute(
        """
        SELECT
            AVG(valor)
        FROM
            comissao_colaborador
        WHERE
            presente = TRUE
            AND EXTRACT(YEAR FROM data) = %s
            AND EXTRACT(MONTH FROM data) = %s
        """,
        (
            ano,
            mes,
        ),
    )

    resultado = cursor.fetchone()

    media_individual = float(
        resultado[0] or 0
    )


    # ==========================================================
    # Acumulado de presença integral
    # ==========================================================

    cursor.execute(
        """
        SELECT
            COALESCE(
                MAX(total_colaborador),
                0
            )
        FROM
        (
            SELECT
                colaborador_id,
                SUM(valor) AS total_colaborador

            FROM
                comissao_colaborador

            WHERE
                presente = TRUE
                AND EXTRACT(YEAR FROM data) = %s
                AND EXTRACT(MONTH FROM data) = %s

            GROUP BY colaborador_id
        ) t
        """,
        (
            ano,
            mes,
        ),
    )

    resultado = cursor.fetchone()

    acumulado_presenca_integral = float(
        resultado[0] or 0
    )


    # ==========================================================
    # Cálculos
    # ==========================================================

    comissao_total = taxa_servico * 0.80

    if dias_comissao > 0:
        media_diaria = comissao_total / dias_comissao
    else:
        media_diaria = 0



    # ==========================================================
    # Projeção final
    # ==========================================================

    dias_mes = calendar.monthrange(
        ano,
        mes,
    )[1]


    hoje = date.today()

    if ano == hoje.year and mes == hoje.month:
        dias_restantes_mes = dias_mes - hoje.day
    else:
        dias_restantes_mes = 0


    projecao_final = (
        acumulado_presenca_integral
        +
        (
            media_individual
            * dias_restantes_mes
        )
    )

    cursor.close()
    conn.close()

    return {
        "taxa_servico": taxa_servico,
        "comissao_total": comissao_total,
        "media_diaria": media_diaria,
        "media_individual": media_individual,
        "projecao_final": projecao_final,
    }






