from data.drive_loader import conectar_drive, listar_arquivos

FOLDER_ID = "1C0SSV4vrFhY9L1jYhpW7Mc8PzCVJGgmo"

service = conectar_drive()

arquivos = listar_arquivos(service, FOLDER_ID)

print("\nArquivos encontrados:\n")

for arq in arquivos:
    print(f"Nome: {arq['name']} | ID: {arq['id']}")