import os
import time

def aguardar_comando():
    input("\nPressione ENTER para voltar ao menu...")


def iniciar_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")

        print("DADOS SCADA CAFE - CINEMA")
        print("-----------------------------------")
        print("1 Faturamento por Mês")
        print("2 Faturamento por Dia")
        print("3 Média Fat por Dia da Semana")
        print("x Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            print("\nFaturamento por mês (em breve)")
            aguardar_comando()

        elif escolha == "2":
            print("\nFaturamento por dia (em breve)")
            aguardar_comando()

        elif escolha == "3":
            print("\nMédia por dia da semana (em breve)")
            aguardar_comando()

        elif escolha == "x":
            break

        else:
            print("Opção inválida")
            time.sleep(1)