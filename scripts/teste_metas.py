from services.metas import (
    ler_planilha_metas,
    preparar_planilha_metas,
    montar_dataframe_importacao,
    validar_importacao_metas,
    importar_metas
)

# ==========================================
# LEITURA DA PLANILHA
# ==========================================

resultado = ler_planilha_metas(
    "data/input/modelo_plan_metas_dados_junho.xlsx"
)

# ==========================================
# PREPARAÇÃO DOS DADOS
# ==========================================

df = preparar_planilha_metas(
    resultado["dados"]
)

# ==========================================
# MONTAGEM DO DATAFRAME
# ==========================================

df = montar_dataframe_importacao(
    df,
    2026,
    resultado["mes"]
)

# ==========================================
# VALIDAÇÃO
# ==========================================

status = validar_importacao_metas(df)

print("STATUS DA VALIDAÇÃO")
print(status)

# ==========================================
# IMPORTAÇÃO
# ==========================================

if status["valido"]:

    resultado_importacao = importar_metas(df)

    print()
    print("RESULTADO DA IMPORTAÇÃO")
    print(resultado_importacao)

else:

    print()
    print("Importação cancelada.")
    print(status["erro"])