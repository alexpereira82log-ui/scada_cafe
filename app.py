from menu.menu import iniciar_menu
from data.loader import carregar_dados
from data.tratamento import tratar_dados
from services.calculos import calcular_metricas


def obter_input_usuario():
    """
    Captura e valida o input do usuário (ano e mês).
    """

    while True:
        try:
            ano = int(input("Digite o Ano (ex: 2026): ").strip())
            mes = int(input("Digite o Mês (1-12): ").strip())

            if mes < 1 or mes > 12:
                print("❌ Mês inválido. Digite um valor entre 1 e 12.\n")
                continue

            return ano, mes

        except ValueError:
            print("❌ Entrada inválida. Digite apenas números.\n")


if __name__ == "__main__":

    # ============================================================
    # 1. CARREGAR DADOS
    # ============================================================
    dados = carregar_dados()

    # ============================================================
    # 2. TRATAR DADOS
    # ============================================================
    dados = tratar_dados(dados)

    # ============================================================
    # 3. INPUT DO USUÁRIO
    # ============================================================
    ano, mes = obter_input_usuario()

    # ============================================================
    # 4. CALCULAR MÉTRICAS
    # ============================================================
    metricas = calcular_metricas(dados, ano, mes)

    # ============================================================
    # 5. INICIAR MENU
    # ============================================================
    iniciar_menu(dados, ano, mes, metricas)