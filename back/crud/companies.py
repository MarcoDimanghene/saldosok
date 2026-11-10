from fastapi import HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas

# ==========================================
# CRUD EMPRESAS (Clientes/Proveedores)
# ==========================================

# Mapeo de campos del schema (inglés) a las columnas de la DB (español)
# Se usa tanto al crear como al actualizar para que el nombre del campo
# del JSON nunca se confunda con el nombre real de la columna.
MAPEO_CAMPOS = {
    "tax_id": "cuit",
    "legal_name": "razon_social",
    "tax_condition": "condicion_iva",
    "condicion_fiscal": "condicion_iva",
    "address": "domicilio",
    "banco_principal": "banco_principal",
    "cbu_propio": "cbu_propio",
    "alias_propio": "alias_propio",
    "localidad": "localidad",
    "provincia": "provincia",
    "banco": "banco",
    "cbu_cvu": "cbu_cvu",
    "alias_cbu": "alias_cbu",
    "titular_cuenta": "titular_cuenta",
    "categoria_servicio": "categoria_servicio",
    "dias_credito": "dias_credito",
    "contacto_nombre": "contacto_nombre",
    "email_1": "email_1",
    "email_2": "email_2",
    "telefono_1": "telefono_1",
    "telefono_2": "telefono_2",
    "observaciones": "observaciones",
    "is_client": "es_cliente",
    "is_supplier": "es_proveedor",
    "is_issuer": "es_emisor",
}

# 1. Buscar empresa por CUIT (Dentro del contexto del Tenant)
def get_company_by_tax_id(db: Session, tenant_id: int, tax_id: str):
    return (
        db.query(models.Company)
        .filter(models.Company.tenant_id == tenant_id, models.Company.cuit == tax_id)
        .first() # Se agregan los paréntesis ()
    )

# 2. Crear Empresa (Inyectando el tenant_id)
def create_company(db: Session, tenant_id: int, company: schemas.CompanyCreate):
    # Convertimos los datos del Schema a diccionario
    company_data = company.model_dump(exclude_none=True)

    # Traducimos los nombres del schema a las columnas reales de la DB
    datos = {MAPEO_CAMPOS.get(k, k): v for k, v in company_data.items()}

    # Inyectamos obligatoriamente el tenant_id de la sesión activa
    db_company = models.Company(**datos, tenant_id=tenant_id)
    
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

# 3. Listar empresas (Solo las del Tenant activo)
def get_companies(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Company)
        .filter(models.Company.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# 4. Buscar empresa por nombre (Filtrado por Tenant)
def get_company_by_name(db: Session, tenant_id: int, name: str, limit: int = 10):
    search = f"%{name}%"
    return (
        db.query(models.Company)
        .filter(
            models.Company.tenant_id == tenant_id,
            models.Company.razon_social.ilike(search)
        )
        .limit(limit)
        .all()
    )

# 5. Editar Empresa (Asegurando que pertenezca al Tenant)
def update_company(db: Session, tenant_id: int, company_id: int, company_data: schemas.CompanyUpdate):
    # Verificamos que coincidan id Y tenant_id
    db_company = (
        db.query(models.Company)
        .filter(models.Company.id == company_id, models.Company.tenant_id == tenant_id)
        .first()
    )
    if not db_company:
        return None

    update_dict = company_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key in MAPEO_CAMPOS:
            nombre_columna = MAPEO_CAMPOS[key]
            setattr(db_company, nombre_columna, value)

    db.commit()
    db.refresh(db_company)
    return db_company

# 6. Eliminar Empresa (Asegurando que pertenezca al Tenant)
def delete_company(db: Session, tenant_id: int, company_id: int):
    db_company = (
        db.query(models.Company)
        .filter(models.Company.id == company_id, models.Company.tenant_id == tenant_id)
        .first()
    )

    if not db_company:
        return False
    if db_company.es_emisor:
        raise HTTPException(
            status_code=400,
            detail="El emisor se administra desde el perfil de organización.",
        )

    # Si la empresa tiene facturas asociadas, la DB no nos deja borrarla
    # (constraint de integridad). Mejor avisamos ANTES con un error claro
    # que dejar que Postgres tire un 500.
    tiene_facturas = (
        db.query(models.SalesInvoice.id)
        .filter(
            (models.SalesInvoice.cliente_id == company_id)
            | (models.SalesInvoice.emisor_id == company_id)
        )
        .first()
    ) or (
        db.query(models.PurchaseInvoice.id)
        .filter(models.PurchaseInvoice.proveedor_id == company_id)
        .first()
    )
    if tiene_facturas:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar: la empresa tiene facturas asociadas."
        )

    db.delete(db_company)
    db.commit()
    return True