from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from back.crud import companies
from back import models
from database.database import get_db
from database.security import get_current_tenant_admin, get_current_user
import back.schemas as schemas

router = APIRouter(
  prefix = "/companies",
  tags = ["Companies"],
)


def _company_visibility(query, current_user: models.User):
    if current_user.is_tenant_admin:
        return query
    if current_user.perfil == "venta":
        return query.filter(
            or_(models.Company.es_cliente.is_(True), models.Company.es_emisor.is_(True))
        )
    if current_user.perfil == "compra":
        return query.filter(
            or_(models.Company.es_proveedor.is_(True), models.Company.es_emisor.is_(True))
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Tu perfil no tiene permiso para consultar empresas.",
    )


def _company_response(company: models.Company, current_user: models.User):
    if current_user.is_tenant_admin or (
        current_user.perfil == "compra" and company.es_proveedor
    ):
        return company
    return schemas.CompanyResponse(
        id=company.id,
        cuit=company.cuit,
        razon_social=company.razon_social,
        condicion_iva=company.condicion_iva,
        condicion_fiscal=company.condicion_fiscal,
        domicilio=company.domicilio,
        localidad=company.localidad,
        provincia=company.provincia,
        dias_credito=company.dias_credito,
        dias_cobro=company.dias_cobro,
        es_cliente=company.es_cliente,
        es_proveedor=False,
        es_emisor=company.es_emisor,
    )


def _validate_company_creation(company: schemas.CompanyCreate, current_user: models.User):
    if current_user.is_tenant_admin:
        return
    if current_user.perfil == "venta":
        valid = company.is_client and not company.is_supplier and not company.is_issuer
        message = "Venta solo puede cargar clientes."
    elif current_user.perfil == "compra":
        valid = company.is_supplier and not company.is_client and not company.is_issuer
        message = "Compra solo puede cargar proveedores."
    else:
        valid = False
        message = "Tu perfil no tiene permiso para crear empresas."
    if not valid:
        raise HTTPException(status_code=403, detail=message)


def _validate_company_update(
    company: schemas.CompanyUpdate,
    existing: models.Company,
    current_user: models.User,
):
    if current_user.is_tenant_admin:
        return
    if current_user.perfil == "venta":
        if not existing.es_cliente:
            raise HTTPException(status_code=404, detail="Empresa no encontrada.")
        allowed_fields = {
            "tax_id", "legal_name", "tax_condition", "condicion_fiscal",
            "address", "localidad", "provincia", "dias_credito", "dias_cobro",
            "contacto_nombre", "email_1", "email_2", "telefono_1", "telefono_2",
            "observaciones",
        }
        detail = "Venta solo puede editar datos de clientes."
    elif current_user.perfil == "compra":
        if not existing.es_proveedor:
            raise HTTPException(status_code=404, detail="Empresa no encontrada.")
        allowed_fields = set(schemas.CompanyUpdate.model_fields).difference(
            {"is_client", "is_supplier", "is_issuer"}
        )
        detail = "Compra solo puede editar datos de proveedores."
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu perfil no tiene permiso para editar empresas.",
        )

    if company.model_fields_set.difference(allowed_fields):
        raise HTTPException(status_code=403, detail=detail)


@router.post("/", response_model = schemas.CompanyResponse)
def creteate_company(company: schemas.CompanyCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  _validate_company_creation(company, current_user)
  # Verificamos duplicidad por CUIT dentro del tenant
  db_company = None
  if company.tax_id:
      db_company = companies.get_company_by_tax_id(db, tenant_id=current_user.tenant_id, tax_id=company.tax_id)
  if db_company:
        raise HTTPException(status_code=400, detail="El CUIT ya está registrado")

  created = companies.create_company(db=db, tenant_id=current_user.tenant_id, company=company)
  return _company_response(created, current_user)

@router.get("/", response_model=list[schemas.CompanyResponse])
def read_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = _company_visibility(
        db.query(models.Company).filter(
            models.Company.tenant_id == current_user.tenant_id
        ),
        current_user,
    )
    lista_empresas = (
        query.order_by(models.Company.razon_social)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_company_response(company, current_user) for company in lista_empresas]


@router.get("/cuit/{tax_id}", response_model=schemas.CompanyResponse)
def read_company_by_cuit(tax_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
# 1. Buscamos en la base de datos usando tu función del CRUD
    query = _company_visibility(
        db.query(models.Company).filter(
            models.Company.tenant_id == current_user.tenant_id,
            models.Company.cuit == tax_id,
        ),
        current_user,
    )
    db_company = query.first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
# 3. Si existe, devolvemos los datos
    return _company_response(db_company, current_user)
@router.get("/search", response_model=list[schemas.CompanyResponse])
def search_companies(name: str = "", db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 1. Si el usuario no escribió nada, devolvemos lista vacía rápido
    if not name.strip():
        return []

    # 2. Buscamos en el CRUD (que ahora usa .ilike() y devuelve una lista)
    query = _company_visibility(
        db.query(models.Company).filter(
            models.Company.tenant_id == current_user.tenant_id,
            models.Company.razon_social.ilike(f"%{name.strip()}%"),
        ),
        current_user,
    )
    return [
        _company_response(company, current_user)
        for company in query.order_by(models.Company.razon_social).limit(10).all()
    ]
@router.patch("/{company_id}", response_model=schemas.CompanyResponse)
def update_company_route(company_id: int, company: schemas.CompanyUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    existing = (
        db.query(models.Company)
        .filter(
            models.Company.id == company_id,
            models.Company.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if existing is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    _validate_company_update(company, existing, current_user)
    role_fields = {"is_client", "is_supplier", "is_issuer"}
    if "tax_id" in company.model_fields_set or role_fields.intersection(company.model_fields_set):
        tax_id = company.tax_id if "tax_id" in company.model_fields_set else existing.cuit
        is_supplier = company.is_supplier if company.is_supplier is not None else existing.es_proveedor
        is_client = company.is_client if company.is_client is not None else existing.es_cliente
        is_issuer = company.is_issuer if company.is_issuer is not None else existing.es_emisor
        if not tax_id and not (is_supplier and not is_client and not is_issuer):
            raise HTTPException(
                status_code=422,
                detail="El CUIT/CUIL solo puede omitirse para proveedores.",
            )

    if "tax_id" in company.model_fields_set and company.tax_id:
        duplicate = companies.get_company_by_tax_id(
            db,
            tenant_id=current_user.tenant_id,
            tax_id=company.tax_id,
        )
        if duplicate and duplicate.id != company_id:
            raise HTTPException(status_code=400, detail="El CUIT ya está registrado")

    # 1. Llamamos a la función del CRUD pasándole el ID y los datos nuevos
    db_company = companies.update_company(db, tenant_id=current_user.tenant_id, company_id=company_id, company_data=company)

    # 2. Si el CRUD nos devolvió None, es porque la empresa no existía
    if db_company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # 3. Si todo salió bien, devolvemos la empresa actualizada
    return _company_response(db_company, current_user)

@router.delete("/{company_id}")
def delete_company_route(company_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_tenant_admin)):
    # 1. Ejecutamos el borrado en el CRUD
    exito = companies.delete_company(db, tenant_id=current_user.tenant_id, company_id=company_id)

    # 2. Si devolvió False, tiramos el 404
    if not exito:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # 3. Si borró bien, devolvemos un mensaje de confirmación corto
    return {"detail": "Empresa eliminada correctamente"}
