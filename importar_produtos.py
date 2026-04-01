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
# TRATAMENTO DOS DADOS
# ==========================================================

# ✅ Usar coluna mes diretamente
if "mes" not in df.columns:
    raise Exception("Coluna 'mes' não encontrada no arquivo")

df["mes"] = pd.to_datetime(df["mes"], errors="coerce")

# Produto obrigatório
if "produto" not in df.columns:
    raise Exception("Coluna 'produto' não encontrada")

# Corrigir números com vírgula
colunas_numericas = ["qtd", "valor_unit", "valor_total"]

for col in colunas_numericas:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Remover inválidos
df = df.dropna(subset=["mes", "produto"])

# ==========================================================
# CONEXÃO
# ==========================================================
conn = get_connection()
cursor = conn.cursor()

# ==========================================================
# INSERT
# ==========================================================
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO venda_produtos (
            mes,
            produto,
            qtd,
            valor_unit,
            valor_total
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        row["mes"],
        row["produto"],
        row.get("qtd", 0),
        row.get("valor_unit", 0),
        row.get("valor_total", 0)
    ))

# ==========================================================
# FINALIZAR
# ==========================================================
conn.commit()
conn.close()

print("✅ Importação concluída com sucesso!")