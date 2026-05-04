import pandas as pd
from database.connection import get_connection


def tratar_meta(valor):
    if pd.isna(valor):
        return None

    # Se já for número (float/int), retorna direto
    if isinstance(valor, (int, float)):
        return float(valor)

    # Se for string no padrão BR
    valor = str(valor).replace(".", "").replace(",", ".")
    return float(valor)


def inserir_metas(caminho_arquivo):

    # =========================
    # CARREGAR EXCEL
    # =========================
    df = pd.read_excel(caminho_arquivo)

    # =========================
    # TRATAMENTO
    # =========================
    df["data"] = pd.to_datetime(df["data"]).dt.date
    df["meta"] = df["meta"].apply(tratar_meta)

    # =========================
    # CONEXÃO
    # =========================
    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # UPDATE NO BANCO
    # =========================
    for _, row in df.iterrows():

        cursor.execute("""
            UPDATE base_fat
            SET meta = %s
            WHERE data = %s
        """, (
            row["meta"],
            row["data"]
        ))

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Metas inseridas com sucesso!")


if __name__ == "__main__":
    inserir_metas("data/input/metas.xlsx")