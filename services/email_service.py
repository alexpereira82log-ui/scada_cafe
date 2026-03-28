import smtplib
from email.message import EmailMessage
import os

from senha_email import senha_app  # mantém seu padrão atual


EMAIL_REMETENTE = "alex.pereira82log@gmail.com"
EMAIL_DESTINOS = ["alex.barista@icloud.com"]


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