import os
import time

from services.analises import (
    faturamento_por_mes,
    faturamento_por_dia,
    top_produtos,
    perdas_por_motivo,
    perdas_por_mes,
    comissao_por_colaborador,
    calcular_comissao_projecoes
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

    falta_meta = metricas["meta"] - metricas["total_fat"]
    diferenca_ticket = metricas["ticket_necessario"] - metricas["ticket_medio"]

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

    print(f"\nMédia de comissão atual: R$ {resultado['media']:,.2f}")
    print(f"Projeção de comissão individual: R$ {resultado['projecao']:,.2f}")

    print("-" * 50)


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
        print("x - Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            mostrar_faturamento_mes(dados, ano)
            aguardar_comando()

        elif escolha == "2":
            mostrar_faturamento_dia(dados, ano, mes)
            aguardar_comando()

        elif escolha == "3":
            mostrar_projecoes(metricas)
            aguardar_comando()

        elif escolha == "4":
            mostrar_top_produtos(dados, ano)
            aguardar_comando()

        elif escolha == "5":
            mostrar_perdas_mes(dados, ano)
            aguardar_comando()

        elif escolha == "6":
            mostrar_perdas_motivo(dados, ano, mes)
            aguardar_comando()

        elif escolha == "7":
            mostrar_comissao_projecoes(dados, ano, mes, metricas)
            aguardar_comando()

        elif escolha.lower() == "x":
            break

        else:
            print("Opção inválida")
            time.sleep(1)