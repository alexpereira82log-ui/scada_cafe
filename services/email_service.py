import os
import smtplib
from email.message import EmailMessage


def enviar_email_com_anexo(arquivo):

    EMAIL = os.getenv("EMAIL_USER")
    SENHA = os.getenv("EMAIL_PASS")

    if not EMAIL or not SENHA:
        raise Exception("Credenciais de email não configuradas.")

    msg = EmailMessage()
    msg["Subject"] = "Relatório de Comissão"
    msg["From"] = EMAIL
    msg["To"] = "alex.barista@icloud.com"

    msg.set_content(
        "Segue em anexo o relatório de comissão do período selecionado."
    )

    with open(arquivo, "rb") as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL, SENHA)
            smtp.send_message(msg)

        print("📧 Email enviado com sucesso!")

    except Exception as e:
        print("❌ Erro ao enviar email:")
        print(e)