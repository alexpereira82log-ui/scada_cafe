import pandas as pd
from database.connection import get_connection

# ================================
# CONFIG
# ================================
ARQUIVO = "metas.xlsx"

# ================================
# 1. LER EXCEL
# ================================
df = pd.read_excel(ARQUIVO)

# ================================
# 2. TRATAR DATA
# ================================
df["data"] = pd.to_datetime(df["data"], errors="coerce")
df = df.dropna(subset=["data"])
df["data"] = df["data"].dt.strftime("%Y-%m-%d")

# ================================
# 3. TRATAR META (VERSÃO ROBUSTA)
# ================================

def tratar_meta(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    # Se já veio como número correto (caso raro)
    try:
        return float(valor)
    except:
        pass

    # Remove milhar e ajusta decimal
    valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except:
        return None


df["meta"] = df["meta"].apply(tratar_meta)
df["meta"] = df["meta"].round(2)

# 🔥 VALIDAÇÃO DE ESCALA (AQUI)
if df["meta"].max() > 10000:
    print("⚠️ Possível erro de escala detectado")

# ================================
# 3. VALIDAÇÃO
# ================================
print("\n🔍 Tipos:")
print(df.dtypes)

print("\n🔍 Pré-visualização:")
print(df.head())

if df["meta"].isnull().any():
    print("\n❌ Erro: valores inválidos encontrados:")
    print(df[df["meta"].isnull()])
    exit()

# ================================
# 4. CONEXÃO
# ================================
conn = get_connection()
cursor = conn.cursor()

# ================================
# 5. UPDATE DIRETO (SEGURO)
# ================================
linhas_atualizadas = 0

for _, row in df.iterrows():
    cursor.execute("""
        UPDATE base_fat
        SET meta = %s
        WHERE data = %s
    """, (
        float(row["meta"]),  # 🔥 garante tipo correto
        row["data"]
    ))

    if cursor.rowcount > 0:
        linhas_atualizadas += 1

# ================================
# 6. FINALIZAR
# ================================
conn.commit()
conn.close()

print(f"\n✅ Metas atualizadas com sucesso! ({linhas_atualizadas} linhas afetadas)")