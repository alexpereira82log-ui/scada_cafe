from datetime import date, timedelta
import calendar

from database.connection import get_connection


DIAS_SEMANA = {
    0: "segunda-feira",
    1: "terça-feira",
    2: "quarta-feira",
    3: "quinta-feira",
    4: "sexta-feira",
    5: "sábado",
    6: "domingo",
}


def inserir_proximo_mes():

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # BUSCA A ÚLTIMA DATA E A ÚLTIMA EQUIPE
    # =====================================================

    cursor.execute("""
        SELECT data, equipe
        FROM base_fat
        ORDER BY data DESC
        LIMIT 1
    """)

    ultima_data, ultima_equipe = cursor.fetchone()

    # =====================================================
    # CALCULA O PRÓXIMO MÊS
    # =====================================================

    if ultima_data.month == 12:
        ano = ultima_data.year + 1
        mes = 1
    else:
        ano = ultima_data.year
        mes = ultima_data.month + 1

    qtd_dias = calendar.monthrange(ano, mes)[1]

    equipe = 2 if ultima_equipe == 1 else 1

    inseridos = 0

    # =====================================================
    # GERA TODAS AS DATAS
    # =====================================================

    for dia in range(1, qtd_dias + 1):

        data_atual = date(ano, mes, dia)

        dia_semana = DIAS_SEMANA[data_atual.weekday()]

        cursor.execute("""
            INSERT INTO base_fat (
                data,
                dia_semana,
                equipe
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (data)
            DO NOTHING
        """, (
            data_atual,
            dia_semana,
            equipe
        ))

        equipe = 2 if equipe == 1 else 1
        inseridos += 1

    conn.commit()

    cursor.close()
    conn.close()

    print()
    print("=" * 40)
    print(f"Mês criado: {mes:02d}/{ano}")
    print(f"Dias gerados: {inseridos}")
    print("✅ Processo concluído com sucesso!")
    print("=" * 40)


if __name__ == "__main__":
    inserir_proximo_mes()