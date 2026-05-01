import pandas as pd
from database.connection import get_connection


def inserir_mes(caminho_arquivo):
    
    # =========================
    # CARREGAR EXCEL
    # =========================
    df = pd.read_excel(caminho_arquivo)

    # =========================
    # TRATAMENTO
    # =========================
    df["data"] = pd.to_datetime(df["data"]).dt.date

    # =========================
    # CONEXÃO
    # =========================
    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # INSERT
    # =========================
    for _, row in df.iterrows():

        cursor.execute("""
            INSERT INTO base_fat (data, dia_semana, equipe)
            VALUES (%s, %s, %s)
            ON CONFLICT (data, equipe) DO NOTHING
        """, (
            row["data"],
            row["dia_semana"],
            int(row["equipe"])
        ))

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Dados inseridos com sucesso!")


if __name__ == "__main__":
    inserir_mes("data/input/novo_mes.xlsx")