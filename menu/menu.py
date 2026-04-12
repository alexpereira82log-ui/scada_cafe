import os
import time

from services.analises import comissao_por_dia_colaborador
from services.relatorios import gerar_excel_comissao
from services.email_service import enviar_email_com_anexo


from services.analises import (
    faturamento_por_mes,
    faturamento_por_dia,
    top_produtos,
    perdas_por_motivo,
    perdas_por_mes,
    comissao_por_colaborador,
    calcular_comissao_projecoes
)

from services.relatorios import (
    carregar_relatorio_por_data,
    extrair_resumo_relatorio,
    extrair_cancelamentos,
    formatar_tabela_cancelamentos
)

def aguardar_comando():
    input("\nPressione ENTER para voltar ao menu...")


# ============================================================
# FUNÇÕES DE EXIBIÇÃO
# ============================================================

def mostrar_faturamento_mes(dados, ano):
    df = faturamento_por_mes(dados, ano)
    print("\nFATURAMENTO POR MÊS")
    print(df)


def mostrar_faturamento_dia(dados, ano, mes):
    df = faturamento_por_dia(dados, ano, mes)
    print("\nFATURAMENTO POR DIA")
    print(df)


def mostrar_projecoes(metricas):
    print("\n" + "-" * 50)
    print("PROJEÇÕES E META")

    falta_meta = metricas["falta_meta"]
    diferenca_ticket = metricas["diferenca_ticket"]

    print(f"Falta para meta: R$ {falta_meta:,.2f}")
    print(f"Projeção do mês: R$ {metricas['proj_fat']:,.2f}")
    print(f"Meta diária necessária: R$ {metricas['fat_dia_necessario']:,.2f}")
    print(f"Ticket necessário: R$ {metricas['ticket_necessario']:,.2f}")
    print(f"Diferença ticket: R$ {diferenca_ticket:,.2f}")
    print(f"Dias restantes: {metricas['dias_restantes']}")

    print("-" * 50)


def mostrar_top_produtos(dados, ano):
    df = top_produtos(dados, ano)
    print("\nTOP PRODUTOS")
    print(df.head(10))


def mostrar_perdas_mes(dados, ano):
    df = perdas_por_mes(dados, ano)
    print("\nPERDAS POR MÊS")
    print(df)


def mostrar_perdas_motivo(dados, ano, mes):
    df = perdas_por_motivo(dados, ano, mes)
    print("\nPERDAS POR MOTIVO (MÊS)")
    print(df)


def mostrar_comissao_projecoes(dados, ano, mes, metricas):

    resultado = calcular_comissao_projecoes(dados, ano, mes, metricas)

    print("\n" + "-" * 50)
    print("COMISSÃO E PROJEÇÕES")

    if resultado["df"].empty:
        print("Sem dados de comissão.")
        return

    print("\nCOMISSÃO ACUMULADA POR COLABORADOR")
    print(resultado["df"])

    print(f"\nTotal comissão acumulada: R$ {resultado['total_acumulado']:,.2f}")
    print(f"Média de comissão atual: R$ {resultado['media']:,.2f}")
    print(f"Projeção de comissão individual: R$ {resultado['projecao']:,.2f}")

    print("-" * 50)


def mostrar_relatorio_comissao(dados, ano, mes):

    print("\n📄 GERANDO RELATÓRIO DE COMISSÃO...\n")

    df = comissao_por_dia_colaborador(dados, ano, mes)

    if df.empty:
        print("❌ Sem dados de comissão.")
        return

    arquivo = gerar_excel_comissao(df)

    print(f"✅ Excel gerado: {arquivo}")

    enviar_email_com_anexo(arquivo)

    print("📧 Email enviado com sucesso!")


def mostrar_resumo_relatorio():

    print("\n📄 RESUMO DE RELATÓRIO\n")

    data_input = input("Digite a data (YYYY-MM-DD): ").strip()

    FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"

    texto, info = carregar_relatorio_por_data(data_input, FOLDER_ID)

    if texto is None:
        print(f"❌ {info}")
        return

    print(f"\n✅ Arquivo encontrado: {info}")

    # =========================
    # 📊 EXTRAÇÃO DE DADOS
    # =========================
    dados = extrair_resumo_relatorio(texto)

    cancel_antes = extrair_cancelamentos(texto, "antes")
    cancel_depois = extrair_cancelamentos(texto, "depois")

    tabela_antes = formatar_tabela_cancelamentos(cancel_antes)
    tabela_depois = formatar_tabela_cancelamentos(cancel_depois)

    # =========================
    # 📅 FORMATAÇÃO DATA
    # =========================
    try:
        ano, mes, dia = data_input.split("-")
        data_formatada = f"{dia}/{mes}/{ano}"
    except:
        data_formatada = data_input

    # =========================
    # 📄 RELATÓRIO FINAL
    # =========================
    print("\n" + "=" * 50)
    print("INICIO DO RELATORIO\n")

    print(f"Data: {data_formatada}")
    print(f"Faturamento bruto: {dados['faturamento_bruto']}")
    print(f"Tx. Serv Mesa: {dados['tx_servico']}")
    print(f"TC-Total Cupom: {dados['tc']}")
    print(f"TM-Ticket Medio por Cupom: {dados['tm']}\n")

    print("CANCELAMENTO VENDA MESA (ANTES ENVIAR PRODUCAO):")
    print(tabela_antes)
    print('- Justificativa: "Escreva aqui sua justificativa"\n')

    print("CANCELAMENTO VENDA MESA (DEPOIS ENVIAR PRODUCAO):")
    print(tabela_depois)
    print('- Justificativa: "Escreva aqui sua justificativa"\n')

    print("FIM DO RELATORIO")
    print("=" * 50 + "\n")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def iniciar_menu(dados, ano, mes, metricas):

    while True:
        os.system("cls" if os.name == "nt" else "clear")

        print("DADOS SCADA CAFE - CINEMA")
        print("-----------------------------------")
        print("1 - Faturamento por Mês")
        print("2 - Faturamento por Dia")
        print("3 - Projeções e Meta")
        print("4 - Top Produtos")
        print("5 - Perdas Mês a Mês")
        print("6 - Perdas por Motivo (Mês atual)")
        print("7 - Comissão e Projeções")
        print("8 - Resumo de relatório diário")
        print("9 - Relatório Comissão")
        print("x - Sair")

        escolha = input("Escolha uma opção: ").strip()
        if not escolha:
            print("Entrada vazia")
            time.sleep(1)
            continue

        acoes = {
            "1": lambda: mostrar_faturamento_mes(dados, ano),
            "2": lambda: mostrar_faturamento_dia(dados, ano, mes),
            "3": lambda: mostrar_projecoes(metricas),
            "4": lambda: mostrar_top_produtos(dados, ano),
            "5": lambda: mostrar_perdas_mes(dados, ano),
            "6": lambda: mostrar_perdas_motivo(dados, ano, mes),
            "7": lambda: mostrar_comissao_projecoes(dados, ano, mes, metricas),
            "8": lambda: mostrar_resumo_relatorio(),
            "9": lambda: mostrar_relatorio_comissao(dados, ano, mes),
        }

        if escolha.lower() == "x":
            break

        elif escolha in acoes:
            acoes[escolha]()
            aguardar_comando()

        else:
            print("Opção inválida")
            time.sleep(1)


