# Bibliotecas padrão
import re

# Imports internos
from services.relatorios import (
    carregar_relatorio_por_data,
    extrair_indicadores,
    extrair_produtos_relatorio,
)

from database.connection import get_connection
from services.persistencia import salvar_base_fat


# ==========================================
# PREPARAR BASE_FAT
# ==========================================

def preparar_base_fat(indicadores: dict) -> dict:

    return {
        "faturamento": indicadores["faturamento_bruto"],
        "cupom": indicadores["cupons"],
        "ticket_medio": indicadores["ticket_medio"],
    }


# ==========================================
# PREPARAR COMISSÃO
# ==========================================

def preparar_comissao(indicadores: dict) -> dict:

    return {
        "comiss_dia": indicadores["tx_servico"],
    }


# ==========================================
# PREPARAR PRODUTOS
# ==========================================

def preparar_produtos(df_produtos):

    return df_produtos.copy()


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

    # ==========================================
    # EXTRAÇÃO DOS DADOS DO RELATÓRIO
    # ==========================================

    indicadores = extrair_indicadores(texto)

    df_produtos = extrair_produtos_relatorio(texto)

    # ==========================================
    # PREPARAÇÃO DOS OBJETOS DE DOMÍNIO
    # ==========================================

    base_fat = preparar_base_fat(indicadores)

    comissao_dia = preparar_comissao(indicadores)

    produtos = preparar_produtos(df_produtos)


    return {

        "data": data_arquivo,

        "nome_arquivo": nome_arquivo,

        "base_fat": base_fat,

        "comissao_dia": comissao_dia,

        "produtos": produtos,

    }


# ==========================================
# EXECUTAR IMPORTAÇÃO
# ==========================================

def executar_importacao(data_relatorio: str, folder_id: str):
    """
    Executa todo o processo de importação,
    desde a leitura do relatório até a
    atualização do banco de dados.
    """

    # Extrai e prepara os dados
    dados_importados = importar_relatorio(
        data_relatorio,
        folder_id
    )

    # Abre uma única conexão
    conn = get_connection()

    try:

        linhas = salvar_base_fat(
            conn=conn,
            data=dados_importados["data"],
            base_fat=dados_importados["base_fat"],
        )

        # Confirma todas as alterações
        conn.commit()

        return linhas

    except Exception:

        # Desfaz alterações em caso de erro
        conn.rollback()
        raise

    finally:

        conn.close()


if __name__ == "__main__":

    FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"

    linhas = executar_importacao(
        "2026-06-10",
        FOLDER_ID
    )

    print(
        f"\n✅ Importação concluída. "
        f"{linhas} registro(s) atualizado(s)."
    )