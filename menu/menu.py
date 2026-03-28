import os
import time

from services.analises import (
    faturamento_por_mes,
    faturamento_por_dia,
    top_produtos,
    perdas_por_motivo
)

from services.relatorios import exportar_excel
from services.email_service import enviar_email_com_anexo


def aguardar_comando():
    input("\nPressione ENTER para voltar ao menu...")


# ============================================================
# FUNÇÕES DE EXIBIÇÃO
# ============================================================

def mostrar_resumo(metricas):
    print("\n" + "-" * 50)
    print("RESUMO DO FATURAMENTO")
    print(f"Faturamento Total: R$ {metricas['total_faturamento']:,.2f}")
    print(f"Meta do Mês: R$ {metricas['meta_mes']:,.2f}")
    print(f"% da Meta: {metricas['percentual_meta']:.0%}")
    print(f"Faturamento Médio Dia: R$ {metricas['media_fat_dia']:,.2f}")
    print(f"Ticket Médio: R$ {metricas['ticket_medio']:,.2f}")
    print(f"Média de Cupons: {metricas['media_cupons']:.0f}")
    print("-" * 50)


def mostrar_projecoes(metricas):
    print("\n" + "-" * 50)
    print("PROJEÇÕES E META")
    print(f"Falta para meta: R$ {metricas['falta_para_meta']:,.2f}")
    print(f"Projeção do mês: R$ {metricas['projecao_mes']:,.2f}")
    print(f"Meta diária necessária: R$ {metricas['meta_dia']:,.2f}")
    print(f"Ticket necessário: R$ {metricas['meta_ticket']:,.2f}")
    print(f"Diferença ticket: R$ {metricas['diferenca_ticket']:,.2f}")
    print("-" * 50)


def mostrar_faturamento_mes(dados, ano):
    df = faturamento_por_mes(dados, ano)
    print("\nFATURAMENTO POR MÊS")
    print(df)


def mostrar_faturamento_dia(dados, ano, mes):
    df = faturamento_por_dia(dados, ano, mes)
    print("\nFATURAMENTO POR DIA")
    print(df)


def mostrar_top_produtos(dados, ano):
    df = top_produtos(dados, ano)
    print("\nTOP PRODUTOS")
    print(df.head(10))


def mostrar_perdas(dados, ano, mes):
    df = perdas_por_motivo(dados, ano, mes)
    print("\nPERDAS POR MOTIVO")
    print(df)


def exportar_faturamento_mes(dados, ano):
    from services.analises import faturamento_por_mes

    df = faturamento_por_mes(dados, ano)
    arquivo = exportar_excel(df, "Relatorio_Faturamento_Mes")
    enviar_email_com_anexo(arquivo)


def exportar_top_produtos(dados, ano):
    from services.analises import top_produtos

    df = top_produtos(dados, ano)
    arquivo = exportar_excel(df, "Relatorio_Top_Produtos")
    enviar_email_com_anexo(arquivo)


# ============================================================
# MENU PRINCIPAL
# ============================================================

def iniciar_menu(dados, ano, mes, metricas):

    while True:
        os.system("cls" if os.name == "nt" else "clear")

        print("DADOS SCADA CAFE - CINEMA")
        print("-----------------------------------")
        print("1 - Resumo Faturamento")
        print("2 - Projeções e Meta")
        print("3 - Faturamento por Mês")
        print("4 - Faturamento por Dia")
        print("5 - Top Produtos")
        print("6 - Perdas por Motivo")
        print("7 - Exportar Faturamento por Mês (Excel + Email)")
        print("8 - Exportar Top Produtos (Excel + Email)")
        print("x - Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            mostrar_resumo(metricas)
            aguardar_comando()

        elif escolha == "2":
            mostrar_projecoes(metricas)
            aguardar_comando()

        elif escolha == "3":
            mostrar_faturamento_mes(dados, ano)
            aguardar_comando()

        elif escolha == "4":
            mostrar_faturamento_dia(dados, ano, mes)
            aguardar_comando()

        elif escolha == "5":
            mostrar_top_produtos(dados, ano)
            aguardar_comando()

        elif escolha == "6":
            mostrar_perdas(dados, ano, mes)
            aguardar_comando()

        elif escolha == "7":
            exportar_faturamento_mes(dados, ano)
            aguardar_comando()

        elif escolha == "8":
            exportar_top_produtos(dados, ano)
            aguardar_comando()

        elif escolha == "x":
            break

        else:
            print("Opção inválida")
            time.sleep(1)

