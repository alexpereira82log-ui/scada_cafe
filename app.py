from menu.menu import iniciar_menu
from data.loader import carregar_dados


if __name__ == "__main__":
    dados = carregar_dados()

    # Teste simples
    print("Tabelas carregadas:")
    for nome, df in dados.items():
        print(f"{nome}: {df.shape}")

    input("\nPressione ENTER para iniciar o sistema...")

    iniciar_menu()