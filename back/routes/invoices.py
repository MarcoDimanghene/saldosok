from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from back.crud import invoices
from back import models
from database.database import get_db
from database.security import get_current_user
import back.schemas as schemas

router = APIRouter(
  prefix="/invoices",
  tags=["Invoices"],
)

#============================
#     FACTURAS DE VENTAS
#============================
#CREAR FACTURA DE VENTAS
@router.post("/sales", response_model=schemas.SalesInvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_sales_invoice(invoice: schemas.SalesInvoiceCreate, db: Session= Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Verificamos duplicidad por número dentro del tenant
  existing_invoice = (
    invoices.get_sales_invoice_by_cae(
      db=db,
      tenant_id=current_user.tenant_id,
      cae=invoice.cae,
    )
    if invoice.cae
    else None
  )
  if existing_invoice:
      raise HTTPException(status_code=400, detail="Invoice already exists")
  if invoice.tipo_comprobante in ["nota_credito", "nota_debito"]:
    if not invoice.factura_origen_id:
      raise HTTPException(
        status_code=400,
        detail="Invoice de origen is required"
      )

    sales = invoices.get_sales_invoice(db=db, tenant_id=current_user.tenant_id, invoice_id=invoice.factura_origen_id)
    if not sales:
      raise HTTPException(
        status_code=404,
        detail="Invoice not found"
      )

  return invoices.create_sales_invoice(db=db, tenant_id=current_user.tenant_id, invoice=invoice)

# BUSCAR FACTURAS POR NUMERO
@router.get("/sales/search-number",response_model=list[schemas.SalesInvoiceResponse])
def search_invoices_by_number(digits: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  if not digits.strip():
    return []
  invoices_found = invoices.search_sales_invoices_by_number_end(db=db, tenant_id=current_user.tenant_id, last_digits=digits)
  return invoices_found

#Editar actualizar
@router.patch("/sales/{invoice_id}", response_model=schemas.SalesInvoiceResponse)
def update_sales_invoice_route(invoice_id: int, invoice: schemas.SalesInvoiceUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  db_s_invoice = invoices.update_sales_invoice(db=db, tenant_id=current_user.tenant_id, invoice_id=invoice_id, invoice_update=invoice)
  if db_s_invoice is None:
    raise HTTPException(
      status_code=404,
      detail="The invoice is not exitsts. Please check the id and try again."
    )
  return db_s_invoice
# Listar
@router.get("/sales/list", response_model=list[schemas.SalesInvoiceResponse])
def list_sales_invoices_route(
  skip: int = Query(0, ge=0),
  limit: int = Query(100, ge=1, le=500),
  db: Session = Depends(get_db),
  current_user: models.User = Depends(get_current_user),
):
  invoices_list = invoices.get_listsales_invoices(db=db, tenant_id=current_user.tenant_id, skip=skip, limit=limit)
  return invoices_list


#============================
#     FACTURAS DE COMPRAS
#============================
# CREAR
@router.post("/purchase", response_model=schemas.PurchaseInvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_invoice(invoice: schemas.PurchaseInvoiceCreate, db: Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
  existing_invoice_p = (
    invoices.get_purchase_by_cae(
      db=db,
      tenant_id=current_user.tenant_id,
      cae=invoice.cae,
    )
    if invoice.cae
    else None
  )
  if existing_invoice_p:
      raise HTTPException(status_code=400, detail="Invoice already exists")
  if invoice.tipo_comprobante in ["nota_credito", "nota_debito"]:
    if not invoice.factura_origen_id:
      raise HTTPException(
        status_code=400,
        detail="Invoice de origen is required"
      )
    purchase = invoices.get_purchase_invoice(db=db, tenant_id=current_user.tenant_id, invoice_id=invoice.factura_origen_id)
    if not purchase:
      raise HTTPException(
        status_code=404,
        detail="Invoice not found"
      )

  return invoices.create_purchase_invoice(db=db, tenant_id=current_user.tenant_id, invoice=invoice)


@router.post(
  "/purchase/pending",
  response_model=schemas.PurchaseInvoiceResponse,
  status_code=status.HTTP_201_CREATED,
)
def create_pending_purchase_invoice(
  purchase: schemas.PurchasePendingCreate,
  db: Session = Depends(get_db),
  current_user: models.User = Depends(get_current_user),
):
  return invoices.create_pending_purchase(
    db=db,
    tenant_id=current_user.tenant_id,
    purchase=purchase,
  )


@router.put(
  "/purchase/{invoice_id}/formal-invoice",
  response_model=schemas.PurchaseInvoiceResponse,
)
def complete_pending_purchase_invoice(
  invoice_id: int,
  data: schemas.PurchaseInvoiceComplete,
  db: Session = Depends(get_db),
  current_user: models.User = Depends(get_current_user),
):
  return invoices.complete_pending_purchase(
    db=db,
    tenant_id=current_user.tenant_id,
    invoice_id=invoice_id,
    data=data,
  )


# BUSCAR FACTURAS POR NUMERO
@router.get("/purchase/search-number", response_model=list[schemas.PurchaseInvoiceResponse])
def purchase_invoices_search_number(digits: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  if not digits.strip():
    return[]
  purchase_invoices_found = invoices.search_purchase_invoices_by_number_end(db=db, tenant_id=current_user.tenant_id, last_digits=digits)
  return purchase_invoices_found
# Editar
@router.patch("/purchase/{invoice_id}", response_model=schemas.PurchaseInvoiceResponse)
def update_purchase_invoice_route(invoice_id: int, invoice: schemas.PurchaseInvoiceUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  db_p_invoice = invoices.update_purchase_invoice(db=db, tenant_id=current_user.tenant_id, invoice_id=invoice_id, invoice_update=invoice)
  if db_p_invoice is None:
    raise HTTPException(
      status_code=404,
      detail="The invoice is not exitsts. Please check the id and try again."
    )
  return db_p_invoice

# Listar
@router.get("/purchase/list", response_model=list[schemas.PurchaseInvoiceResponse])
def list_purchase_invoices_route(
  skip: int = Query(0, ge=0),
  limit: int = Query(100, ge=1, le=500),
  db: Session = Depends(get_db),
  current_user: models.User = Depends(get_current_user),
):
  invoices_list = invoices.get_listpurchase_invoice(db=db, tenant_id=current_user.tenant_id, skip=skip, limit=limit)
  return invoices_list
