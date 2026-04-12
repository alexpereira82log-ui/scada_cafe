import smtplib
from email.message import EmailMessage
import os

from senha_email import senha_app  # mantém seu padrão atual


EMAIL_REMETENTE = "alex.pereira82log@gmail.com"
EMAIL_DESTINOS = ["alex.barista@icloud.com"]

# ====================================
# ENVIAR EMAIL COM ANEXO:
# ====================================
def enviar_email_com_anexo(caminho_arquivo: str):
    try:
        msg = EmailMessage()

        nome_arquivo = os.path.basename(caminho_arquivo)

        msg["Subject"] = f"Relatório - {nome_arquivo}"
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = ", ".join(EMAIL_DESTINOS)

        msg.set_content("Segue relatório em anexo.")

        with open(caminho_arquivo, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=nome_arquivo
            )

        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, senha_app)
        servidor.send_message(msg)
        servidor.quit()

        print("Email enviado com sucesso!")

    except Exception as e:
        print(f"Erro ao enviar email: {e}")




# ====================================
# ENVIAR EMAIL COMISSÃO:
# ====================================
def enviar_email_com_anexo(arquivo):

    EMAIL = "alex.pereira82log@gmail.com"
    SENHA = senha_app

    msg = EmailMessage()
    msg["Subject"] = "Relatório de Comissão"
    msg["From"] = EMAIL
    msg["To"] = "alex.barista@icloud.com"

    msg.set_content("Segue em anexo o relatório de comissão.")

    with open(arquivo, "rb") as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, SENHA)
        smtp.send_message(msg)