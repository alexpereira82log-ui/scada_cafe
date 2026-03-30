import pandas as pd
import sqlite3
import os

# ==============================
# CONFIGURAÇÕES
# ==============================

CAMINHO_BANCO = "faturamento_scada.db"
TABELA = "base_fat"
ARQUIVO_EXCEL = "novo_mes.xlsx"


def importar_excel_para_sqlite():
    print(f"\nProcessando arquivo: {ARQUIVO_EXCEL}")

    if not os.path.exists(ARQUIVO_EXCEL):
        print(f"Arquivo não encontrado: {ARQUIVO_EXCEL}")
        return

    # ==============================
    # LEITURA DO EXCEL
    # ==============================

    df = pd.read_excel(ARQUIVO_EXCEL)

    print("Colunas encontradas:", df.columns.tolist())

    # Padronizar nomes
    df.columns = [col.lower().strip() for col in df.columns]

    # ==============================
    # VALIDAR COLUNAS
    # ==============================

    colunas_esperadas = ["data", "dia_semana", "equipe"]

    colunas_faltando = [col for col in colunas_esperadas if col not in df.columns]

    if colunas_faltando:
        raise ValueError(
            f"Colunas faltando: {colunas_faltando} | "
            f"Colunas encontradas: {df.columns.tolist()}"
        )

    # Manter apenas as colunas necessárias
    df = df[colunas_esperadas]

    # ==============================
    # TRATAMENTO
    # ==============================

    # Data no padrão correto
    df["data"] = pd.to_datetime(df["data"]).dt.strftime("%Y-%m-%d")

    # Garantir tipos
    df["dia_semana"] = df["dia_semana"].astype(str)
    df["equipe"] = pd.to_numeric(df["equipe"])

    # ==============================
    # CONEXÃO COM BANCO
    # ==============================

    conn = sqlite3.connect(CAMINHO_BANCO)

    # ==============================
    # EVITAR DUPLICIDADE
    # ==============================

    datas_existentes = pd.read_sql(
        f"SELECT data FROM {TABELA}",
        conn
    )

    df = df[~df["data"].isin(datas_existentes["data"])]

    if df.empty:
        print("Nenhum dado novo para inserir.")
        conn.close()
        return

    # ==============================
    # INSERÇÃO (IMPORTANTE)
    # ==============================

    df.to_sql(
        TABELA,
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

    print(f"{len(df)} registros inseridos com sucesso!")


if __name__ == "__main__":
    importar_excel_para_sqlite()