# app/services/email_service.py

from email.message import EmailMessage
from flask import current_app
import smtplib


def send_email(
    to,
    subject,
    body,
    from_email=None,
    from_name=None
):
    """
    Envia e-mail usando SMTP global,
    com remetente dinâmico por empresa.
    """

    msg = EmailMessage()

    # ==========================
    # REMETENTE
    # ==========================
    if from_email:
        if from_name:
            msg["From"] = f"{from_name} <{from_email}>"
        else:
            msg["From"] = from_email
    else:
        msg["From"] = current_app.config["MAIL_DEFAULT_SENDER"]

    # ==========================
    # DESTINATÁRIO
    # ==========================
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    # ==========================
    # SMTP
    # ==========================
    server = smtplib.SMTP(
        current_app.config["MAIL_SERVER"],
        current_app.config["MAIL_PORT"]
    )

    if current_app.config.get("MAIL_USE_TLS", True):
        server.starttls()

    server.login(
        current_app.config["MAIL_USERNAME"],
        current_app.config["MAIL_PASSWORD"]
    )

    server.send_message(msg)
    server.quit()
