from menu.menu import iniciar_menu
from data.loader import carregar_dados
from data.tratamento import tratar_dados
from services.calculos import calcular_metricas


if __name__ == "__main__":
    dados = carregar_dados()
    dados = tratar_dados(dados)

    ano = int(input("Digite o Ano: "))
    mes = int(input("Digite o Mês: "))

    metricas = calcular_metricas(dados, ano, mes)

    iniciar_menu(dados, ano, mes, metricas)