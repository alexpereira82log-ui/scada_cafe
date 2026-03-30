import pandas as pd
import sqlite3

# ================================
# CONFIGURAÇÕES
# ================================
CAMINHO_EXCEL = "dados_excel/metas.xlsx"
BANCO_DADOS = "faturamento_scada.db"
TABELA_DESTINO = "base_fat"
TABELA_TEMP = "temp_meta_import"

# ================================
# 1. LER EXCEL COMO TEXTO
# ================================
df = pd.read_excel(CAMINHO_EXCEL, dtype=str)

# ================================
# 2. TRATAR DADOS
# ================================

# Data
df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%Y-%m-%d")

# Meta (AGORA SIMPLES E CORRETO)
df["meta"] = (
    df["meta"]
    .astype(str)
    .str.strip()
    .str.replace(",", ".", regex=False)  # só troca decimal
)

df["meta"] = pd.to_numeric(df["meta"], errors="coerce")

df["meta"] = df["meta"].round(2)

# ================================
# 3. VALIDAÇÃO
# ================================
print("\n🔍 Pré-visualização:")
print(df.head())

if df["meta"].isnull().any():
    print("\n❌ Erro: valores inválidos encontrados:")
    print(df[df["meta"].isnull()])
    exit()

# ================================
# 4. CONECTAR AO SQLITE
# ================================
conn = sqlite3.connect(BANCO_DADOS)
cursor = conn.cursor()

# ================================
# 5. TABELA TEMPORÁRIA
# ================================
cursor.execute(f"DROP TABLE IF EXISTS {TABELA_TEMP};")

cursor.execute(f"""
CREATE TABLE {TABELA_TEMP} (
    data TEXT PRIMARY KEY,
    meta REAL
);
""")

# ================================
# 6. INSERIR DADOS
# ================================
df.to_sql(TABELA_TEMP, conn, if_exists="append", index=False)

# ================================
# 7. UPDATE (SUBSTITUI VALORES)
# ================================
cursor.execute(f"""
UPDATE {TABELA_DESTINO}
SET meta = (
    SELECT t.meta
    FROM {TABELA_TEMP} t
    WHERE t.data = {TABELA_DESTINO}.data
)
WHERE data IN (SELECT data FROM {TABELA_TEMP});
""")

conn.commit()

# ================================
# 8. LIMPEZA
# ================================
cursor.execute(f"DROP TABLE {TABELA_TEMP};")
conn.commit()

conn.close()

print("\n✅ Atualização concluída com sucesso!")