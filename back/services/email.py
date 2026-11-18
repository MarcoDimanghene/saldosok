def _send_message() -> None:
    raise RuntimeError("El envío de correo está desactivado.")


def send_verification_email(recipient: str, token: str) -> None:
    _send_message()


def send_password_reset_email(recipient: str, token: str) -> None:
    _send_message()


def send_user_invitation_email(recipient: str, token: str) -> None:
    _send_message()
