from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from back import models
from back.crud import payments as crud_payments
from database.database import get_db
from database.security import get_current_user
import back.schemas as schemas
from typing import List

router = APIRouter(
  prefix="/payments",
  tags=["payments"],
)

#=====================================================================
# 1. ENDPOINTS PARA COBROS (Sales Collections)
#=====================================================================
@router.post("/collection", response_model=schemas.CollectionResponse,status_code=status.HTTP_201_CREATED)
def create_new_collection(collection: schemas.CollectionCreate, db: Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
  """
    Registra un nuevo cobro para una factura de venta y actualiza su 'status'.
  """
  return crud_payments.create_collection(db=db, tenant_id=current_user.tenant_id, collection=collection)
@router.get("/collection/invoice/{invoice_id}", response_model=List[schemas.CollectionResponse])
def list_collections_by_invoice(invoice_id: int, db: Session= Depends(get_db), current_user: models.User = Depends(get_current_user)):
  """
    Trae la lista de todos los cobros aplicados a una factura de venta específica.
  """
  return crud_payments.get_collections_by_invoice_id(db=db, tenant_id=current_user.tenant_id, invoice_id=invoice_id)
@router.put("/collection/{collection_id}", response_model=schemas.CollectionResponse)
def update_existing_collection(collection_id: int, collection_update: schemas.CollectionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Modifica un cobro existente y recalcula el 'status' de la factura de venta.
    """
    return crud_payments.update_collection(db=db, tenant_id=current_user.tenant_id, collection_id=collection_id, collection_update=collection_update)


@router.delete("/collection/{collection_id}", status_code=status.HTTP_200_OK)
def delete_existing_collection(collection_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Elimina un cobro y recalcula el 'status' de la factura de venta.
    """
    return crud_payments.delete_collection(db=db, tenant_id=current_user.tenant_id, collection_id=collection_id)
#=====================================================================
# 2. ENDPOINTS PARA PAGOS (Purchase Payments)
#=====================================================================
@router.post("/payment", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_new_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Registra un nuevo pago para una factura de compra y actualiza su 'status'.
    """
    return crud_payments.create_payment(db=db, tenant_id=current_user.tenant_id, payment=payment)


@router.get("/payment/invoice/{invoice_id}", response_model=List[schemas.PaymentResponse])
def list_payments_by_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Trae la lista de todos los pagos aplicados a una factura de compra específica.
    """
    return crud_payments.get_payments_by_invoice_id(db=db, tenant_id=current_user.tenant_id, invoice_id=invoice_id)


@router.put("/payment/{payment_id}", response_model=schemas.PaymentResponse)
def update_existing_payment(payment_id: int, payment_update: schemas.PaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Modifica un pago existente y recalcula el 'status' de la factura de compra.
    """
    return crud_payments.update_payment(db=db, tenant_id=current_user.tenant_id, payment_id=payment_id, payment_update=payment_update)


@router.delete("/payment/{payment_id}", status_code=status.HTTP_200_OK)
def delete_existing_payment(payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Elimina un pago y recalcula el 'status' de la factura de compra.
    """
    return crud_payments.delete_payment(db=db, tenant_id=current_user.tenant_id, payment_id=payment_id)
