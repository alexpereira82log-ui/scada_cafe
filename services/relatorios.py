import pandas as pd
import re

from data.drive_loader import conectar_drive, listar_arquivos, baixar_arquivo

# =========================
# 📥 EXPORTAÇÃO
# =========================
def exportar_excel(df: pd.DataFrame, nome_arquivo: str) -> str:
    df = df.copy()

    colunas_numericas = df.select_dtypes(include=["float", "int"]).columns
    for col in colunas_numericas:
        df[col] = df[col].round(2)

    caminho = f"{nome_arquivo}.xlsx"

    df.to_excel(caminho, index=False)

    print(f"Arquivo gerado: {caminho}")

    return caminho


# =========================
# 📊 NOVO: PARSE DO RELATÓRIO TXT
# =========================
def extrair_indicadores(texto):

    def buscar_valor(label):
        match = re.search(rf"{label}.*?:\s+([\d\.,-]+)", texto)
        if match:
            return float(match.group(1).replace(".", "").replace(",", "."))
        return 0

    dados = {
        "faturamento_bruto": buscar_valor("Faturamento Bruto"),
        "resultado_operacional": buscar_valor("RES. OPERACIONAL"),
        "sangria": buscar_valor("Sangria"),
        "troco": buscar_valor("Troco"),
    }

    # Ticket médio
    match_tm = re.search(r"TM-Ticket Medio por Cupom...:\s+([\d\.,]+)", texto)
    dados["ticket_medio"] = float(match_tm.group(1).replace(",", ".")) if match_tm else 0

    # Cupons
    match_tc = re.search(r"TC-Total Cupom..............:\s+(\d+)", texto)
    dados["cupons"] = int(match_tc.group(1)) if match_tc else 0

    return dados


# =========================
# 📊 RELATORIO POR DATA:
# =========================
def carregar_relatorio_por_data(data_input: str, folder_id: str):

    service = conectar_drive()
    arquivos = listar_arquivos(service, folder_id)

    if not arquivos:
        return None, "Nenhum arquivo encontrado no Drive."

    for arq in arquivos:
        if data_input in arq["name"]:
            texto = baixar_arquivo(service, arq["id"])
            return texto, arq["name"]

    return None, f"Nenhum relatório encontrado para a data {data_input}"