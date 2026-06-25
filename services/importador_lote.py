from services.importador import executar_importacao

FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"

datas = [
    "2026-06-01",
    "2026-06-02",
    "2026-06-03",
    "2026-06-04",
    "2026-06-05",
    "2026-06-06",
    "2026-06-07",
    "2026-06-08",
    "2026-06-09",
    "2026-06-10",
]

for data in datas:

    try:

        resultado = executar_importacao(
            data,
            FOLDER_ID
        )

        print(
            f"✅ {data} | "
            f"base_fat={resultado['base_fat']} | "
            f"comissao={resultado['comissao_dia']} | "
            f"produtos={resultado['produtos']}"
        )

    except Exception as e:

        print(f"❌ {data} | ERRO: {e}")