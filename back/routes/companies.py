from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from back.crud import companies
from back import models
from database.database import get_db
from database.security import get_current_user
import back.schemas as schemas

router = APIRouter(
  prefix = "/companies",
  tags = ["Companies"],
)

@router.post("/", response_model = schemas.CompanyResponse)
def creteate_company(company: schemas.CompanyCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Verificamos duplicidad por CUIT dentro del tenant
  db_company = None
  if company.tax_id:
      db_company = companies.get_company_by_tax_id(db, tenant_id=current_user.tenant_id, tax_id=company.tax_id)
  if db_company:
        raise HTTPException(status_code=400, detail="El CUIT ya está registrado")

  return companies.create_company(db=db, tenant_id=current_user.tenant_id, company=company)

@router.get("/", response_model=list[schemas.CompanyResponse])
def read_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    lista_empresas = companies.get_companies(db, tenant_id=current_user.tenant_id, skip=skip, limit=limit)
    return lista_empresas


@router.get("/cuit/{tax_id}", response_model=schemas.CompanyResponse)
def read_company_by_cuit(tax_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
# 1. Buscamos en la base de datos usando tu función del CRUD
    db_company = companies.get_company_by_tax_id(db, tenant_id=current_user.tenant_id, tax_id=tax_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
# 3. Si existe, devolvemos los datos
    return db_company
@router.get("/search", response_model=list[schemas.CompanyResponse])
def search_companies(name: str = "", db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 1. Si el usuario no escribió nada, devolvemos lista vacía rápido
    if not name.strip():
        return []

    # 2. Buscamos en el CRUD (que ahora usa .ilike() y devuelve una lista)
    lista_empresas = companies.get_company_by_name(db, tenant_id=current_user.tenant_id, name=name)

    # 3. Devolvemos los resultados
    return lista_empresas
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
    return db_company

@router.delete("/{company_id}")
def delete_company_route(company_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 1. Ejecutamos el borrado en el CRUD
    exito = companies.delete_company(db, tenant_id=current_user.tenant_id, company_id=company_id)

    # 2. Si devolvió False, tiramos el 404
    if not exito:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # 3. Si borró bien, devolvemos un mensaje de confirmación corto
    return {"detail": "Empresa eliminada correctamente"}
