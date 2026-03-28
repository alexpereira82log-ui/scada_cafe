import pandas as pd


def exportar_excel(df: pd.DataFrame, nome_arquivo: str) -> str:
    """
    Exporta um DataFrame para Excel com formatação básica.
    """

    df = df.copy()

    # Arredondar colunas numéricas
    colunas_numericas = df.select_dtypes(include=["float", "int"]).columns
    for col in colunas_numericas:
        df[col] = df[col].round(2)

    caminho = f"{nome_arquivo}.xlsx"

    df.to_excel(caminho, index=False)

    print(f"Arquivo gerado: {caminho}")

    return caminho