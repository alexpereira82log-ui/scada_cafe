from services.relatorios import (
    carregar_relatorio_por_data,
    extrair_indicadores,
    extrair_produtos_relatorio,
)

import re

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

    # ==========================================
    # EXTRAIR DATA DO NOME DO ARQUIVO
    # ==========================================

    match = re.search(r"\d{4}-\d{2}-\d{2}", nome_arquivo)

    data_arquivo = match.group() if match else data_relatorio

    if texto is None:
        raise Exception(nome_arquivo)

    indicadores = extrair_indicadores(texto)

    df_produtos = extrair_produtos_relatorio(texto)


    return {

        # ==========================================
        # IDENTIFICAÇÃO
        # ==========================================

        "data": data_arquivo,

        "nome_arquivo": nome_arquivo,

        # ==========================================
        # BASE_FAT
        # ==========================================

        "base_fat": {

            "faturamento": indicadores["faturamento_bruto"],

            "cupom": indicadores["cupons"],

            "ticket_medio": indicadores["ticket_medio"]

        },

        # ==========================================
        # COMISSÃO DO DIA
        # ==========================================

        "comissao_dia": {

            "comiss_dia": indicadores["tx_servico"]

        },

        # ==========================================
        # PRODUTOS
        # ==========================================

        "produtos": df_produtos

    }


if __name__ == "__main__":

    FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"

    resultado = importar_relatorio(
        "2026-06-10",
        FOLDER_ID
    )

    print("\n===== DATA =====")
    print(resultado["data"])

    print("\n===== ARQUIVO =====")
    print(resultado["nome_arquivo"])

    print("\n===== BASE_FAT =====")
    print(resultado["base_fat"])

    print("\n===== COMISSÃO =====")
    print(resultado["comissao_dia"])

    print("\n===== PRODUTOS =====")
    print(resultado["produtos"])