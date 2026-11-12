import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from back import schemas, models, crud
from back.services.email_verification import issue_email_verification
from database.database import get_db
from database.security import (
    get_current_superadmin,
    get_current_user,
    get_password_hash,
)

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"]
)


# -------------------------------------------------------------
# Alta de Tenant + primer usuario admin (solo SuperAdmin)
# -------------------------------------------------------------

@router.post(
    "/register",
    response_model=schemas.TenantRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superadmin)],
)
def register_tenant_with_user(
    register: schemas.TenantRegister,
    db: Session = Depends(get_db),
):
    """Crea la cuenta del titular y su espacio de trabajo inicial."""

    existing_user = db.query(models.User).filter(
        models.User.username == register.username.lower()
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con ese nombre de usuario."
        )
    if db.query(models.User).filter(
        func.lower(models.User.email) == register.email.lower()
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con este correo electrónico."
        )
    if register.dni and db.query(models.User).filter(models.User.dni == register.dni).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con ese DNI.",
        )

    hashed_pass = get_password_hash(register.password)
    tenant, user = crud.create_tenant_with_admin(db=db, register=register, hashed_password=hashed_pass)
    recovery_code = secrets.token_urlsafe(18)
    db.add(models.PasswordRecoveryCode(
        user_id=user.id,
        code_hash=hashlib.sha256(recovery_code.encode()).hexdigest(),
    ))
    db.commit()

    try:
        issue_email_verification(db, user)
    except HTTPException:
        message = (
            "Cuenta creada. No se pudo enviar la confirmación del correo. "
            "Guarda ahora el código de recuperación y vuelve a intentar confirmar el email."
        )
    else:
        message = (
            "Cuenta creada. Confirma tu correo para habilitar la recuperación de contraseña. "
            "Guarda ahora el código de recuperación."
        )

    return {
        "tenant": tenant,
        "user": schemas.UserResponse.model_validate(user).model_dump(),
        "message": message,
        "recovery_code": recovery_code,
    }


@router.post("/verify-email", response_model=schemas.EmailVerificationResponse)
def verify_email(
    request: schemas.EmailVerificationToken,
    db: Session = Depends(get_db),
):
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    verification = (
        db.query(models.EmailVerification)
        .filter(models.EmailVerification.token_hash == token_hash)
        .first()
    )
    if not verification:
        raise HTTPException(status_code=400, detail="El enlace de confirmación no es válido o ya fue utilizado.")

    expires_at = verification.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        db.delete(verification)
        db.commit()
        raise HTTPException(status_code=400, detail="El enlace de confirmación venció. Solicita uno nuevo.")

    user = db.query(models.User).filter(models.User.id == verification.user_id).first()
    if not user:
        db.delete(verification)
        db.commit()
        raise HTTPException(status_code=400, detail="No se encontró la cuenta asociada al enlace.")

    user.is_email_verified = True
    db.delete(verification)
    db.commit()
    return {"message": "Correo confirmado. Ya puedes recuperar tu contraseña por email."}


@router.post("/resend-verification", response_model=schemas.EmailVerificationResponse)
def resend_email_verification(
    request: schemas.EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(func.lower(models.User.email) == request.email.lower()).first()
    if user and not user.is_email_verified:
        _issue_email_verification(db, user)
    return {
        "message": "Si hay una cuenta con ese correo sin confirmar, enviaremos un nuevo enlace."
    }


# -------------------------------------------------------------
# Endpoints de Uso Interno / SuperAdmin
# -------------------------------------------------------------

@router.post(
    "/",
    response_model=schemas.TenantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superadmin)],
)
def create_new_tenant(
    tenant: schemas.TenantCreate,
    db: Session = Depends(get_db),
):
    """Crea una nueva organización (Tenant) en la plataforma."""
    db_tenant = crud.get_tenant_by_cuit(db, cuit=tenant.cuit) if tenant.cuit else None
    if db_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una empresa registrada con ese CUIT."
        )
    return crud.create_tenant(db=db, tenant=tenant)


@router.get(
    "/",
    response_model=List[schemas.TenantResponse],
    dependencies=[Depends(get_current_superadmin)],
)
def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Listado global de empresas (Exclusivo SuperAdmin)."""
    return crud.get_tenants(db=db, skip=skip, limit=limit)


# -------------------------------------------------------------
# Endpoints para el Tenant en sesión
# -------------------------------------------------------------

@router.get("/me", response_model=schemas.TenantResponse)
def get_current_tenant_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Obtiene la información de la empresa a la que pertenece el usuario autenticado."""
    tenant = crud.get_tenant(db=db, tenant_id=current_user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado.")
    return tenant


@router.patch("/me", response_model=schemas.TenantResponse)
def update_current_tenant(
    tenant_update: schemas.TenantUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Actualiza el perfil de la organización del usuario."""
    if not current_user.is_tenant_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador para modificar el perfil.",
        )
    tenant = crud.get_tenant(db, current_user.tenant_id)
    profile_fields = {"cuit", "razon_social", "condicion_iva", "domicilio"}
    if tenant_update.model_fields_set.intersection(profile_fields):
        merged_cuit = tenant_update.cuit if "cuit" in tenant_update.model_fields_set else tenant.cuit
        merged_name = (
            tenant_update.razon_social
            if "razon_social" in tenant_update.model_fields_set
            else tenant.razon_social
        )
        if not merged_cuit or not merged_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Para guardar el perfil fiscal se requieren CUIT y razón social.",
            )
        duplicate = crud.get_tenant_by_cuit(db, cuit=merged_cuit)
        if duplicate and duplicate.id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un perfil de organización con ese CUIT.",
            )

    updated_tenant = crud.update_tenant(
        db=db, 
        tenant_id=current_user.tenant_id, 
        tenant_update=tenant_update
    )
    if not updated_tenant:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
    return updated_tenant