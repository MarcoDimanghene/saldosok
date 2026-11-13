import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from back import models, schemas
from back.services.email import send_password_reset_email
from back.services.audit import record_audit_event
from back.models.user import User
from database.database import get_db
from database.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    login_name = form_data.username.strip().lower()
    user = db.query(User).filter(
        or_(User.username == login_name, User.email == login_name)
    ).first()

    # 2. Validamos que el usuario exista y la contraseña coincida con el hash
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Validamos si el usuario no está desactivado
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    # 4. Generamos el JWT incluyendo el id del usuario (sub) y su tenant_id en los claims
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": user.tenant_id}
    )

    # 5. Retornamos la respuesta requerida por el estándar OAuth2
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password", response_model=schemas.EmailVerificationResponse)
def request_password_reset(
    request: schemas.PasswordResetRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        func.lower(User.email) == request.email.lower(),
        User.is_email_verified.is_(True),
        User.is_active.is_(True),
    ).first()
    if user:
        raw_token = secrets.token_urlsafe(32)
        db.query(models.PasswordReset).filter(
            models.PasswordReset.user_id == user.id
        ).delete()
        db.add(models.PasswordReset(
            user_id=user.id,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        db.commit()
        try:
            send_password_reset_email(user.email, raw_token)
        except (OSError, RuntimeError, smtplib.SMTPException) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo enviar el enlace de recuperación. Intenta nuevamente más tarde.",
            ) from error

    return {
        "message": "Si la cuenta tiene un correo confirmado, enviaremos un enlace para restablecer la contraseña."
    }


@router.post("/reset-password", response_model=schemas.EmailVerificationResponse)
def reset_password(
    request: schemas.PasswordResetToken,
    db: Session = Depends(get_db),
):
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    reset = db.query(models.PasswordReset).filter(
        models.PasswordReset.token_hash == token_hash
    ).first()
    if not reset:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace no es válido o ya fue utilizado.")

    expires_at = reset.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        db.delete(reset)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace venció. Solicita uno nuevo.")

    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user or not user.is_active:
        db.delete(reset)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se encontró una cuenta activa para este enlace.")

    user.hashed_password = get_password_hash(request.new_password)
    user.is_email_verified = True
    record_audit_event(
        db,
        user.tenant_id,
        "password_set",
        "user",
        user.id,
        after_data={"email_verified": True},
        actor_user_id=user.id,
    )
    db.delete(reset)
    db.query(models.PasswordReset).filter(
        models.PasswordReset.user_id == user.id
    ).delete()
    db.commit()
    return {"message": "La contraseña se restableció correctamente."}


@router.post("/recover-with-code", response_model=schemas.EmailVerificationResponse)
def reset_password_with_recovery_code(
    request: schemas.RecoveryCodePasswordReset,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == request.username.strip().lower()).first()
    if not user or not user.is_tenant_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o código de recuperación incorrectos.")

    recovery = db.query(models.PasswordRecoveryCode).filter(
        models.PasswordRecoveryCode.user_id == user.id
    ).first()
    submitted_hash = hashlib.sha256(request.recovery_code.encode()).hexdigest()
    if not recovery or not secrets.compare_digest(recovery.code_hash, submitted_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o código de recuperación incorrectos.")

    user.hashed_password = get_password_hash(request.new_password)
    record_audit_event(
        db,
        user.tenant_id,
        "password_reset",
        "user",
        user.id,
        after_data={"method": "recovery_code"},
        actor_user_id=user.id,
    )
    db.delete(recovery)
    db.flush()
    replacement_code = secrets.token_urlsafe(18)
    db.add(models.PasswordRecoveryCode(
        user_id=user.id,
        code_hash=hashlib.sha256(replacement_code.encode()).hexdigest(),
    ))
    db.query(models.PasswordReset).filter(
        models.PasswordReset.user_id == user.id
    ).delete()
    db.commit()
    return {
        "message": "La contraseña se restableció correctamente. Guarda el nuevo código de recuperación; el anterior ya no sirve.",
        "recovery_code": replacement_code,
    }
