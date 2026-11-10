from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from back import schemas, models, crud
from database.database import get_db
from database.security import (
    get_current_tenant_admin,
    get_current_user,
    get_password_hash,
)
from back.services.email_verification import issue_email_verification


router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)


@router.post("/", response_model=schemas.UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user_for_tenant(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_tenant_admin)
):
    """Crea un usuario dentro del Tenant activo (respetando el límite del plan)."""
    tenant = crud.get_tenant(db=db, tenant_id=current_user.tenant_id)
    limite = crud.get_plan_user_limit(tenant.plan)
    usuarios_actuales = crud.count_users(db=db, tenant_id=current_user.tenant_id)

    if usuarios_actuales >= limite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Tu plan '{tenant.plan}' permite un máximo de {limite} "
                f"usuario{'s' if limite != 1 else ''}. "
                f"Ya tenés {usuarios_actuales}. Mejorá tu plan para agregar más usuarios."
            )
        )

    existing_user = crud.get_user_by_username(db=db, username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con ese nombre de usuario."
        )
    if user.email and db.query(models.User).filter(
        func.lower(models.User.email) == user.email.lower()
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con este correo electrónico."
        )
    if user.dni and db.query(models.User).filter(models.User.dni == user.dni).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con ese DNI.",
        )

    hashed_pass = get_password_hash(user.password)
    created_user = crud.create_user(
        db=db, tenant_id=current_user.tenant_id, user=user, hashed_password=hashed_pass
    )
    try:
        issue_email_verification(db, created_user)
    except HTTPException:
        message = (
            "El usuario se creó, pero no se pudo enviar la confirmación. "
            "Puede solicitar un nuevo enlace desde la pantalla de confirmación."
        )
    else:
        message = "El usuario se creó. Debe confirmar su correo para habilitar la recuperación."
    return {"user": created_user, "message": message}


@router.get("/", response_model=List[schemas.UserResponse])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_tenant_admin)
):
    """Lista todos los usuarios pertenecientes al Tenant activo."""
    return crud.get_users(db=db, tenant_id=current_user.tenant_id, skip=skip, limit=limit)


@router.get("/me", response_model=schemas.UserResponse)
def read_user_me(current_user: models.User = Depends(get_current_user)):
    """Obtiene el perfil del usuario autenticado actual."""
    return current_user


@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_tenant_admin)
):
    """Obtiene los detalles de un usuario específico dentro de la empresa."""
    db_user = crud.get_user(db=db, tenant_id=current_user.tenant_id, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return db_user


@router.patch("/{user_id}", response_model=schemas.UserResponse)
def update_user_by_id(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_tenant_admin)
):
    """Actualiza un usuario específico dentro de la empresa."""
    if "email" in user_update.model_fields_set and not user_update.email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El correo electrónico no puede quitarse de una cuenta.",
        )
    if "username" in user_update.model_fields_set and not user_update.username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El nombre de usuario no puede estar vacío.",
        )

    existing = db.query(models.User).filter(
        models.User.username == (user_update.username or "").lower(),
        models.User.id != user_id,
    ).first() if user_update.username else None
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con ese nombre de usuario.",
        )

    if user_update.email:
        existing_email = db.query(models.User).filter(
            func.lower(models.User.email) == user_update.email.lower(),
            models.User.id != user_id,
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una cuenta con este correo electrónico.",
            )
    if "dni" in user_update.model_fields_set and user_update.dni:
        existing_dni = db.query(models.User).filter(
            models.User.dni == user_update.dni,
            models.User.id != user_id,
        ).first()
        if existing_dni:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una cuenta con ese DNI.",
            )

    hashed_pass = None
    if user_update.password:
        hashed_pass = get_password_hash(user_update.password)

    db_user = crud.update_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=user_id,
        user_update=user_update,
        hashed_password=hashed_pass
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_tenant_admin)
):
    """Elimina a un usuario dentro del Tenant activo."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No podés eliminar tu propia cuenta de usuario activo."
        )

    deleted = crud.delete_user(db=db, tenant_id=current_user.tenant_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {"detail": "Usuario eliminado correctamente."}
