from services.metas import (
    ler_planilha_metas,
    preparar_planilha_metas,
    montar_dataframe_importacao,
    validar_importacao_metas
)

resultado = ler_planilha_metas(
    "data/input/modelo_plan_metas_dados_junho.xlsx"
)

df = preparar_planilha_metas(
    resultado["dados"]
)

df = montar_dataframe_importacao(
    df,
    2026,
    resultado["mes"]
)

status = validar_importacao_metas(df)

print(status)