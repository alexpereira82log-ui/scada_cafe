import pandas as pd
from database.connection import get_connection

# ==========================================================
# CONFIG
# ==========================================================
ARQUIVO = "produtos.xlsx"

# ==========================================================
# LER EXCEL
# ==========================================================
df = pd.read_excel(ARQUIVO)

print("COLUNAS ORIGINAIS:", df.columns)

# ==========================================================
# NORMALIZAR COLUNAS
# ==========================================================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("ã", "a")
    .str.replace("ç", "c")
)

print("COLUNAS NORMALIZADAS:", df.columns)

# ==========================================================
# TRATAMENTO
# ==========================================================

# Data (vem da coluna mes)
df["data"] = pd.to_datetime(df["data"], errors="coerce")

# Corrigir números com vírgula
colunas_numericas = [
    "qtd", "valor_unit", "valor_total",
    "perc_total_venda", "mtc"
]

for col in colunas_numericas:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Remover inválidos
df = df.dropna(subset=["data", "produto"])

# ==========================================================
# CONEXÃO
# ==========================================================
conn = get_connection()
cursor = conn.cursor()

# ==========================================================
# LIMPAR MÊS (IMPORTANTE)
# ==========================================================
data_min = df["data"].min()
data_max = df["data"].max()

cursor.execute("""
    DELETE FROM venda_produtos
    WHERE data BETWEEN %s AND %s
""", (data_min, data_max))

# ==========================================================
# INSERT
# ==========================================================
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO venda_produtos (
            data, cod, produto, un,
            qtd, valor_unit, valor_total,
            perc_total_venda, mtc
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["data"],
        row.get("cod"),
        row["produto"],
        row.get("un"),
        row.get("qtd"),
        row.get("valor_unit"),
        row.get("valor_total"),
        row.get("perc_total_venda"),
        row.get("mtc")
    ))

# ==========================================================
# FINALIZAR
# ==========================================================
conn.commit()
conn.close()

print("✅ Importação concluída com sucesso!")