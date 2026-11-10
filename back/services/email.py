import smtplib
from email.message import EmailMessage

from database.config import settings


def send_verification_email(recipient: str, token: str) -> None:
    if not all((settings.SMTP_HOST, settings.SMTP_FROM)):
        raise RuntimeError("El envío de correo no está configurado.")

    verification_url = f"{settings.FRONTEND_URL.rstrip('/')}/verify-email?token={token}"
    message = EmailMessage()
    message["Subject"] = "Confirma tu correo electrónico - Saldos Ok"
    message["From"] = settings.SMTP_FROM
    message["To"] = recipient
    message.set_content(
        "Confirma tu correo electrónico para habilitar la recuperación de contraseña por email:\n\n"
        f"{verification_url}\n\n"
        "El enlace vence en 24 horas. Si no solicitaste esta cuenta, ignora este mensaje."
    )

    if settings.SMTP_PORT == 465:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
            server.send_message(message)
        return

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
        server.send_message(message)


def send_password_reset_email(recipient: str, token: str) -> None:
    if not all((settings.SMTP_HOST, settings.SMTP_FROM)):
        raise RuntimeError("El envío de correo no está configurado.")

    reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
    message = EmailMessage()
    message["Subject"] = "Restablece tu contraseña - Saldos Ok"
    message["From"] = settings.SMTP_FROM
    message["To"] = recipient
    message.set_content(
        "Recibimos una solicitud para restablecer la contraseña de tu cuenta de Saldos Ok:\n\n"
        f"{reset_url}\n\n"
        "El enlace vence en una hora. Si no solicitaste este cambio, ignora este mensaje."
    )

    if settings.SMTP_PORT == 465:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
            server.send_message(message)
        return

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
        server.send_message(message)
