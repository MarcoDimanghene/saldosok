from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas
from back.services.audit import record_audit_event, snapshot_fields

_USER_AUDIT_FIELDS = (
    "nombre",
    "username",
    "email",
    "is_active",
    "is_email_verified",
    "is_tenant_admin",
)

# ==========================================
# CRUD Tenants
# ==========================================

# 1. Buscar tenant por ID
def get_tenant(db: Session, tenant_id: int):
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()

# 1b. Buscar usuario por email DENTRO de un Tenant específico
def get_user_by_email_and_tenant(db: Session, tenant_id: int, email: str):
    return (
        db.query(models.User)
        .filter(models.User.tenant_id == tenant_id, func.lower(models.User.email) == email.lower())
        .first()
    )


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username.lower()).first()


# 2. Crear Usuario (Usando Schema y Hash ya procesado)
def create_user(db: Session, tenant_id: int, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        nombre=user.nombre,
        dni=user.dni,
        username=user.username.lower(),
        email=user.email.lower(),
        hashed_password=hashed_password,
        is_active=user.is_active if hasattr(user, "is_active") else True,
        is_email_verified=False,
        is_tenant_admin=False,
        tenant_id=tenant_id,
    )
    db.add(db_user)
    db.flush()
    record_audit_event(
        db,
        tenant_id,
        "created",
        "user",
        db_user.id,
        after_data=snapshot_fields(db_user, _USER_AUDIT_FIELDS),
    )
    db.commit()
    db.refresh(db_user)
    return db_user

# 3. Listar usuarios del Tenant
def get_users(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.User)
        .filter(models.User.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# 3b. Contar los usuarios del Tenant para validar su límite
def count_users(db: Session, tenant_id: int) -> int:
    return db.query(models.User).filter(models.User.tenant_id == tenant_id).count()

# 4. Buscar usuario por ID y Tenant
def get_user(db: Session, tenant_id: int, user_id: int):
    return (
        db.query(models.User)
        .filter(models.User.id == user_id, models.User.tenant_id == tenant_id)
        .first()
    )

# 5. Editar Usuario
def update_user(
    db: Session, 
    tenant_id: int, 
    user_id: int, 
    user_update: schemas.UserUpdate,
):
    db_user = get_user(db, tenant_id=tenant_id, user_id=user_id)
    if not db_user:
        return None

    before_data = snapshot_fields(db_user, _USER_AUDIT_FIELDS)
    # Extraemos solo los campos enviados (exclude_unset=True evita sobrescribir con None)
    update_data = user_update.model_dump(exclude_unset=True)
    if "username" in update_data and update_data["username"] is not None:
        update_data["username"] = update_data["username"].lower()
    if "email" in update_data:
        if update_data["email"] is not None:
            update_data["email"] = update_data["email"].lower()
        if update_data["email"] != db_user.email:
            update_data["is_email_verified"] = update_data["email"] is None
            db.query(models.EmailVerification).filter(
                models.EmailVerification.user_id == db_user.id
            ).delete()
            db.query(models.PasswordReset).filter(
                models.PasswordReset.user_id == db_user.id
            ).delete()

    for key, value in update_data.items():
        if hasattr(db_user, key) and key != "tenant_id": # Impedimos cambiar el tenant
            setattr(db_user, key, value)

    record_audit_event(
        db,
        tenant_id,
        "updated",
        "user",
        db_user.id,
        before_data=before_data,
        after_data=snapshot_fields(db_user, _USER_AUDIT_FIELDS),
    )
    db.commit()
    db.refresh(db_user)
    return db_user

# 6. Eliminar Usuario
def delete_user(db: Session, tenant_id: int, user_id: int) -> bool:
    db_user = get_user(db, tenant_id=tenant_id, user_id=user_id)
    if db_user:
        before_data = snapshot_fields(db_user, _USER_AUDIT_FIELDS)
        record_audit_event(
            db,
            tenant_id,
            "deleted",
            "user",
            db_user.id,
            before_data=before_data,
        )
        db.delete(db_user)
        db.commit()
        return True
    return False