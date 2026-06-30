import calendar
import pandas as pd
from datetime import date
from database.connection import get_connection

# ==========================================
# STATUS DO MÊS
# ==========================================

def obter_status_mes(ano, mes):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS dias_cadastrados,
            COUNT(meta) AS dias_com_meta,
            COALESCE(SUM(meta), 0) AS meta_mensal
        FROM base_fat
        WHERE EXTRACT(YEAR FROM data) = %s
          AND EXTRACT(MONTH FROM data) = %s
    """, (ano, mes))

    dias_cadastrados, dias_com_meta, meta_mensal = cursor.fetchone()

    conn.close()

    return {
        "calendario": dias_cadastrados > 0,
        "dias_cadastrados": dias_cadastrados,
        "dias_com_meta": dias_com_meta,
        "meta_mensal": float(meta_mensal)
    }

# ==========================================
# VERIFICAR CALENDÁRIO
# ==========================================

def calendario_existe(ano, mes):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM base_fat
        WHERE EXTRACT(YEAR FROM data) = %s
          AND EXTRACT(MONTH FROM data) = %s
    """, (ano, mes))

    quantidade = cursor.fetchone()[0]

    conn.close()

    return quantidade > 0

# ==========================================
# OBTÉM O PRÓXIMO MÊS
# ==========================================

MESES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

MESES_NUMERO = {
    "Janeiro": 1,
    "Fevereiro": 2,
    "Março": 3,
    "Abril": 4,
    "Maio": 5,
    "Junho": 6,
    "Julho": 7,
    "Agosto": 8,
    "Setembro": 9,
    "Outubro": 10,
    "Novembro": 11,
    "Dezembro": 12,
}

def obter_proximo_mes():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            data,
            equipe
        FROM base_fat
        ORDER BY data DESC
        LIMIT 1
    """)

    ultima_data, ultima_equipe = cursor.fetchone()

    conn.close()

    if ultima_data.month == 12:
        ano = ultima_data.year + 1
        mes = 1
    else:
        ano = ultima_data.year
        mes = ultima_data.month + 1

    equipe_inicial = 2 if ultima_equipe == 1 else 1

    return {
        "ano": ano,
        "mes": mes,
        "nome_mes": MESES[mes],
        "qtd_dias": calendar.monthrange(ano, mes)[1],
        "equipe_inicial": equipe_inicial
    }

# ==========================================
# ABRIR NOVO MÊS
# ==========================================

DIAS_SEMANA = {
    0: "segunda-feira",
    1: "terça-feira",
    2: "quarta-feira",
    3: "quinta-feira",
    4: "sexta-feira",
    5: "sábado",
    6: "domingo",
}


def abrir_novo_mes(simular=False):

    proximo = obter_proximo_mes()

    ano = proximo["ano"]
    mes = proximo["mes"]
    equipe = proximo["equipe_inicial"]
    qtd_dias = proximo["qtd_dias"]

    # Segurança
    if calendario_existe(ano, mes):

        raise ValueError(
            f"O calendário de {proximo['nome_mes']}/{ano} já foi criado."
        )

    conn = get_connection()
    cursor = conn.cursor()

    equipe_inicial = equipe
    dias_inseridos = 0

    try:

        for dia in range(1, qtd_dias + 1):

            data_atual = date(ano, mes, dia)

            dia_semana = DIAS_SEMANA[data_atual.weekday()]

            if not simular:

                cursor.execute("""
                    INSERT INTO base_fat (
                        data,
                        dia_semana,
                        equipe
                    )
                    VALUES (%s, %s, %s)
                """, (
                    data_atual,
                    dia_semana,
                    equipe
                ))

            equipe = 2 if equipe == 1 else 1

            dias_inseridos += 1

        if not simular:

            conn.commit()

    except Exception:
        if not simular:
            conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()

    return {

        "nome_mes": proximo["nome_mes"],
        "ano": ano,
        "dias_inseridos": dias_inseridos,
        "qtd_dias": qtd_dias,
        "equipe_inicial": equipe_inicial,
        "simulacao": simular

    }

# ==========================================
# LER PLANILHA DE METAS
# ==========================================

def ler_planilha_metas(arquivo_excel):

    xls = pd.ExcelFile(arquivo_excel)

    nomes_meses = list(MESES.values())

    nome_aba = None

    for aba in xls.sheet_names:

        if aba.strip().capitalize() in nomes_meses:

            nome_aba = aba
            break

    if nome_aba is None:

        raise ValueError(
            "Nenhuma aba correspondente a um mês foi encontrada."
        )

    df = pd.read_excel(
        arquivo_excel,
        sheet_name=nome_aba,
        header=4
    )

    return {

        "nome_mes": nome_aba,
        "mes": MESES_NUMERO[nome_aba],
        "dados": df

    }

# ==========================================
# PREPARAR PLANILHA DE METAS
# ==========================================

def preparar_planilha_metas(df):

    df = df[
        [
            "Dia",
            "Meta"
        ]
    ].copy()

    df["Dia"] = pd.to_numeric(
        df["Dia"],
        errors="coerce"
    )

    df = df.dropna(subset=["Dia"])

    df["Dia"] = df["Dia"].astype(int)

    return df

# ==========================================
# MONTAR DATAFRAME DE IMPORTAÇÃO
# ==========================================

def montar_dataframe_importacao(df, ano, mes):

    df = df.copy()

    df["data"] = pd.to_datetime({
        "year": ano,
        "month": mes,
        "day": df["Dia"]
    }).dt.date

    df = df[
        [
            "data",
            "Meta"
        ]
    ]

    df = df.rename(
        columns={
            "Meta": "meta"
        }
    )

    return df

# ==========================================
# VALIDAR IMPORTAÇÃO DE METAS
# ==========================================

def validar_importacao_metas(df):

    ano = df["data"].iloc[0].year
    mes = df["data"].iloc[0].month

    status = obter_status_mes(
        ano,
        mes
    )

    if not status["calendario"]:

        return {

            "valido": False,
            "erro": "O calendário deste mês ainda não foi criado."

        }

    return {

        "valido": True,
        "dias_planilha": len(df),
        "dias_banco": status["dias_cadastrados"],
        "meta_mensal": float(df["meta"].sum())

    }

# ==========================================
# IMPORTAR METAS
# ==========================================

def importar_metas(df):

    conn = get_connection()
    cursor = conn.cursor()

    registros_atualizados = 0

    try:

        for _, row in df.iterrows():

            cursor.execute("""
                UPDATE base_fat
                SET meta = %s
                WHERE data = %s
            """, (
                row["meta"],
                row["data"]
            ))

            registros_atualizados += cursor.rowcount

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()

    return {

        "registros_atualizados": registros_atualizados,
        "meta_mensal": float(df["meta"].sum())

    }