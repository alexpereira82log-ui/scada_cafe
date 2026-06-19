from services.relatorios import (
    carregar_relatorio_por_data,
    extrair_indicadores,
    extrair_produtos_relatorio,
)


def importar_relatorio(data_relatorio: str, folder_id: str):
    """
    Importa um relatório diário do Google Drive
    e retorna seus dados estruturados.
    """

    texto, nome_arquivo = carregar_relatorio_por_data(
        data_relatorio,
        folder_id
    )

    if texto is None:
        raise Exception(nome_arquivo)

    indicadores = extrair_indicadores(texto)

    df_produtos = extrair_produtos_relatorio(texto)

    return {
        "nome_arquivo": nome_arquivo,
        "indicadores": indicadores,
        "produtos": df_produtos
    }


if __name__ == "__main__":

    FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"

    resultado = importar_relatorio(
        "2026-06-10",
        FOLDER_ID
    )

    print("\n===== ARQUIVO =====")
    print(resultado["nome_arquivo"])

    print("\n===== INDICADORES =====")
    print(resultado["indicadores"])

    print("\n===== PRODUTOS =====")
    print(resultado["produtos"].to_string())