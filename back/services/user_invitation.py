import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from back import models
from back.services.audit import record_audit_event
from back.services.email import send_user_invitation_email


def issue_user_invitation(
    db: Session,
    user: models.User,
    action: str = "invitation_sent",
) -> None:
    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    db.query(models.PasswordReset).filter(
        models.PasswordReset.user_id == user.id
    ).delete()
    db.query(models.EmailVerification).filter(
        models.EmailVerification.user_id == user.id
    ).delete()
    db.add(models.PasswordReset(
        user_id=user.id,
        token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
        expires_at=expires_at,
    ))
    db.commit()

    try:
        send_user_invitation_email(user.email, raw_token)
    except (OSError, RuntimeError, smtplib.SMTPException) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "La cuenta se creó, pero no se pudo enviar la invitación. "
                "Puedes volver a enviarla desde la sección Usuarios."
            ),
        ) from error

    record_audit_event(
        db,
        tenant_id=user.tenant_id,
        action=action,
        entity_type="user",
        entity_id=user.id,
        after_data={"email": user.email, "expires_at": expires_at},
    )
    db.commit()
