from sqlalchemy.orm import Session
from typing import Optional, List
from .. import models, schemas

# ==========================================
# CRUD TENANTS
# ==========================================

MAX_USERS_PER_TENANT = 10

# 1. Buscar tenant por CUIT (Útil para validación previa a la creación)
def get_tenant_by_cuit(db: Session, cuit: str) -> Optional[models.Tenant]:
    return db.query(models.Tenant).filter(models.Tenant.cuit == cuit).first()

# 2. Obtener un tenant por ID
def get_tenant(db: Session, tenant_id: int) -> Optional[models.Tenant]:
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()

# 3. Listar tenants (Exclusivo para uso del SuperAdmin)
def get_tenants(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tenant]:
    return db.query(models.Tenant).offset(skip).limit(limit).all()


def _add_primary_issuer(db: Session, tenant: models.Tenant) -> None:
    if not tenant.cuit or not tenant.razon_social:
        return
    db.add(
        models.Company(
            cuit=tenant.cuit,
            razon_social=tenant.razon_social,
            condicion_iva=tenant.condicion_iva,
            domicilio=tenant.domicilio,
            es_emisor=True,
            tenant_id=tenant.id,
        )
    )


# 4. Crear un nuevo tenant
def create_tenant(db: Session, tenant: schemas.TenantCreate) -> models.Tenant:
    # Usamos model_dump() para mapear automáticamente el schema al modelo SQLAlchemy
    db_tenant = models.Tenant(**tenant.model_dump())
    db.add(db_tenant)
    db.flush()
    _add_primary_issuer(db, db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

# 5. Actualizar un tenant
def update_tenant(
    db: Session, tenant_id: int, tenant_update: schemas.TenantUpdate
) -> Optional[models.Tenant]:
    db_tenant = get_tenant(db, tenant_id=tenant_id)
    if not db_tenant:
        return None

    # Sintaxis de Pydantic v2: model_dump(exclude_unset=True)
    update_data = tenant_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tenant, key, value)

    db.commit()
    db.refresh(db_tenant)
    return db_tenant

# 6. Eliminar un tenant (Borrado físico)
def delete_tenant(db: Session, tenant_id: int) -> bool:
    db_tenant = get_tenant(db, tenant_id=tenant_id)
    if db_tenant:
        db.delete(db_tenant)
        db.commit()
        return True
    return False

# 7. Registrar tenant + primer usuario admin (registro público, transacción)
def create_tenant_with_admin(
    db: Session,
    register: schemas.TenantRegister,
    hashed_password: str,
):
    db_tenant = models.Tenant()
    db.add(db_tenant)
    db.flush()

    db_user = models.User(
        nombre=register.nombre,
        dni=register.dni,
        username=register.username.lower(),
        email=register.email.lower(),
        hashed_password=hashed_password,
        is_active=True,
        is_email_verified=False,
        is_tenant_admin=True,
        tenant_id=db_tenant.id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_tenant)
    db.refresh(db_user)
    return db_tenant, db_user