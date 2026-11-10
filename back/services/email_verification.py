import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from back import models
from back.services.email import send_verification_email


def issue_email_verification(db: Session, user: models.User) -> None:
    raw_token = secrets.token_urlsafe(32)
    db.query(models.EmailVerification).filter(
        models.EmailVerification.user_id == user.id
    ).delete()
    db.add(models.EmailVerification(
        user_id=user.id,
        token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    ))
    db.commit()
    try:
        send_verification_email(user.email, raw_token)
    except (OSError, RuntimeError, smtplib.SMTPException) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "No se pudo enviar el correo de confirmación. "
                "Puedes solicitar un nuevo enlace desde la pantalla de confirmación."
            ),
        ) from error
