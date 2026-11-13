from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from back import models, schemas
from back.services.audit import record_audit_event, snapshot_fields
from back.services.invoice_balances import get_adjusted_invoice_total

_COLLECTION_AUDIT_FIELDS = (
    "factura_venta_id",
    "monto",
    "fecha_cobro",
    "metodo_cobro",
    "nro_comprobante",
)
_PAYMENT_AUDIT_FIELDS = (
    "factura_compra_id",
    "monto",
    "fecha_pago",
    "metodo_pago",
    "nro_comprobante",
)

def _invoice_total(db: Session, tenant_id: int, invoice) -> Decimal:
    if (invoice.tipo_comprobante or "factura") != "factura":
        raise HTTPException(
            status_code=400,
            detail="Las notas se aplican al saldo de la factura vinculada y no admiten movimientos propios.",
        )
    return get_adjusted_invoice_total(db, tenant_id, invoice)


def _update_invoice_status(
    invoice,
    amount_paid: Decimal,
    invoice_total: Decimal,
) -> None:
    if amount_paid >= invoice_total:
        invoice.estado = "pagado"
    elif amount_paid > 0:
        invoice.estado = "parcial"
    else:
        invoice.estado = "pendiente"


def _ensure_amount_within_balance(amount: Decimal, balance: Decimal, message: str) -> None:
    if amount <= 0:
        raise HTTPException(status_code=422, detail="El monto debe ser mayor que cero.")
    if balance <= 0:
        raise HTTPException(status_code=400, detail=message)
    if amount > balance:
        raise HTTPException(
            status_code=400,
            detail=f"El monto supera el saldo pendiente (${balance}).",
        )


def _get_locked_sales_invoice(db: Session, tenant_id: int, invoice_id: int):
    return (
        db.query(models.SalesInvoice)
        .filter(
            models.SalesInvoice.tenant_id == tenant_id,
            models.SalesInvoice.id == invoice_id,
        )
        .with_for_update()
        .first()
    )


def _get_locked_purchase_invoice(db: Session, tenant_id: int, invoice_id: int):
    return (
        db.query(models.PurchaseInvoice)
        .filter(
            models.PurchaseInvoice.tenant_id == tenant_id,
            models.PurchaseInvoice.id == invoice_id,
        )
        .with_for_update()
        .first()
    )


def _sales_collected_total(
    db: Session,
    tenant_id: int,
    invoice_id: int,
    excluding_collection_id: int | None = None,
) -> Decimal:
    query = db.query(
        func.coalesce(func.sum(models.SalesCollection.monto), 0)
    ).filter(
        models.SalesCollection.tenant_id == tenant_id,
        models.SalesCollection.factura_venta_id == invoice_id,
    )
    if excluding_collection_id is not None:
        query = query.filter(models.SalesCollection.id != excluding_collection_id)
    return query.scalar()


def _purchase_paid_total(
    db: Session,
    tenant_id: int,
    invoice_id: int,
    excluding_payment_id: int | None = None,
) -> Decimal:
    query = db.query(
        func.coalesce(func.sum(models.PurchasePayment.monto), 0)
    ).filter(
        models.PurchasePayment.tenant_id == tenant_id,
        models.PurchasePayment.factura_compra_id == invoice_id,
    )
    if excluding_payment_id is not None:
        query = query.filter(models.PurchasePayment.id != excluding_payment_id)
    return query.scalar()


def create_collection(db: Session, tenant_id: int, collection: schemas.CollectionCreate):
    invoice = _get_locked_sales_invoice(db, tenant_id, collection.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="La factura de venta no existe.")

    already_collected = _sales_collected_total(db, tenant_id, collection.invoice_id)
    invoice_total = _invoice_total(db, tenant_id, invoice)
    pending_balance = invoice_total - already_collected
    _ensure_amount_within_balance(
        collection.amount,
        pending_balance,
        "Esta factura ya está totalmente cobrada.",
    )

    db_collection = models.SalesCollection(
        tenant_id=tenant_id,
        factura_venta_id=collection.invoice_id,
        monto=collection.amount,
        fecha_cobro=collection.collection_date,
        metodo_cobro=collection.collection_method,
        nro_comprobante=collection.receipt_number,
        notas=collection.notes,
    )
    db.add(db_collection)
    invoice_status_before = invoice.estado
    _update_invoice_status(
        invoice,
        already_collected + collection.amount,
        invoice_total,
    )
    db.flush()
    record_audit_event(
        db,
        tenant_id,
        "created",
        "sales_collection",
        db_collection.id,
        before_data={"invoice_status": invoice_status_before},
        after_data={
            **snapshot_fields(db_collection, _COLLECTION_AUDIT_FIELDS),
            "invoice_status": invoice.estado,
        },
    )
    db.commit()
    db.refresh(db_collection)
    return db_collection


def get_collections_by_invoice_id(db: Session, tenant_id: int, invoice_id: int):
    return (
        db.query(models.SalesCollection)
        .filter(
            models.SalesCollection.tenant_id == tenant_id,
            models.SalesCollection.factura_venta_id == invoice_id,
        )
        .order_by(
            models.SalesCollection.fecha_cobro.desc(),
            models.SalesCollection.id.desc(),
        )
        .all()
    )


def update_collection(
    db: Session,
    tenant_id: int,
    collection_id: int,
    collection_update: schemas.CollectionCreate,
):
    db_collection = (
        db.query(models.SalesCollection)
        .filter(
            models.SalesCollection.tenant_id == tenant_id,
            models.SalesCollection.id == collection_id,
        )
        .first()
    )
    if not db_collection:
        raise HTTPException(status_code=404, detail="El cobro no existe.")

    invoice = _get_locked_sales_invoice(
        db, tenant_id, db_collection.factura_venta_id
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="La factura de venta no existe.")

    before_data = {
        **snapshot_fields(db_collection, _COLLECTION_AUDIT_FIELDS),
        "invoice_status": invoice.estado,
    }
    other_collections = _sales_collected_total(
        db,
        tenant_id,
        invoice.id,
        excluding_collection_id=db_collection.id,
    )
    invoice_total = _invoice_total(db, tenant_id, invoice)
    pending_balance = invoice_total - other_collections
    _ensure_amount_within_balance(
        collection_update.amount,
        pending_balance,
        "Esta factura ya está totalmente cobrada.",
    )

    db_collection.monto = collection_update.amount
    db_collection.fecha_cobro = collection_update.collection_date
    db_collection.metodo_cobro = collection_update.collection_method
    db_collection.nro_comprobante = collection_update.receipt_number
    db_collection.notas = collection_update.notes
    _update_invoice_status(
        invoice,
        other_collections + collection_update.amount,
        invoice_total,
    )

    record_audit_event(
        db,
        tenant_id,
        "updated",
        "sales_collection",
        db_collection.id,
        before_data=before_data,
        after_data={
            **snapshot_fields(db_collection, _COLLECTION_AUDIT_FIELDS),
            "invoice_status": invoice.estado,
        },
    )
    db.commit()
    db.refresh(db_collection)
    return db_collection


def delete_collection(db: Session, tenant_id: int, collection_id: int):
    db_collection = (
        db.query(models.SalesCollection)
        .filter(
            models.SalesCollection.tenant_id == tenant_id,
            models.SalesCollection.id == collection_id,
        )
        .first()
    )
    if not db_collection:
        raise HTTPException(status_code=404, detail="El cobro no existe.")

    invoice = _get_locked_sales_invoice(
        db, tenant_id, db_collection.factura_venta_id
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="La factura de venta no existe.")

    before_data = {
        **snapshot_fields(db_collection, _COLLECTION_AUDIT_FIELDS),
        "invoice_status": invoice.estado,
    }
    db.delete(db_collection)
    db.flush()
    _update_invoice_status(
        invoice,
        _sales_collected_total(db, tenant_id, invoice.id),
        _invoice_total(db, tenant_id, invoice),
    )
    record_audit_event(
        db,
        tenant_id,
        "deleted",
        "sales_collection",
        db_collection.id,
        before_data=before_data,
        after_data={"invoice_status": invoice.estado},
    )
    db.commit()
    return {"detail": "Cobro eliminado correctamente y estado de factura actualizado."}


def create_payment(db: Session, tenant_id: int, payment: schemas.PaymentCreate):
    invoice = _get_locked_purchase_invoice(db, tenant_id, payment.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="La factura no existe.")

    already_paid = _purchase_paid_total(db, tenant_id, payment.invoice_id)
    invoice_total = _invoice_total(db, tenant_id, invoice)
    pending_balance = invoice_total - already_paid
    _ensure_amount_within_balance(
        payment.amount,
        pending_balance,
        "Esta factura ya está totalmente pagada.",
    )

    db_payment = models.PurchasePayment(
        tenant_id=tenant_id,
        factura_compra_id=payment.invoice_id,
        monto=payment.amount,
        fecha_pago=payment.payment_date,
        metodo_pago=payment.payment_method,
        nro_comprobante=payment.receipt_number,
        notas=payment.notes,
    )
    db.add(db_payment)
    invoice_status_before = invoice.estado
    _update_invoice_status(
        invoice,
        already_paid + payment.amount,
        invoice_total,
    )
    db.flush()
    record_audit_event(
        db,
        tenant_id,
        "created",
        "purchase_payment",
        db_payment.id,
        before_data={"invoice_status": invoice_status_before},
        after_data={
            **snapshot_fields(db_payment, _PAYMENT_AUDIT_FIELDS),
            "invoice_status": invoice.estado,
        },
    )
    db.commit()
    db.refresh(db_payment)
    return db_payment


def get_payments_by_invoice_id(db: Session, tenant_id: int, invoice_id: int):
    return (
        db.query(models.PurchasePayment)
        .filter(
            models.PurchasePayment.tenant_id == tenant_id,
            models.PurchasePayment.factura_compra_id == invoice_id,
        )
        .order_by(
            models.PurchasePayment.fecha_pago.desc(),
            models.PurchasePayment.id.desc(),
        )
        .all()
    )


def update_payment(
    db: Session,
    tenant_id: int,
    payment_id: int,
    payment_update: schemas.PaymentCreate,
):
    db_payment = (
        db.query(models.PurchasePayment)
        .filter(
            models.PurchasePayment.tenant_id == tenant_id,
            models.PurchasePayment.id == payment_id,
        )
        .first()
    )
    if not db_payment:
        raise HTTPException(status_code=404, detail="El pago no existe.")

    invoice = _get_locked_purchase_invoice(
        db, tenant_id, db_payment.factura_compra_id
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="La factura no existe.")

    before_data = {
        **snapshot_fields(db_payment, _PAYMENT_AUDIT_FIELDS),
        "invoice_status": invoice.estado,
    }
    other_payments = _purchase_paid_total(
        db,
        tenant_id,
        invoice.id,
        excluding_payment_id=db_payment.id,
    )
    invoice_total = _invoice_total(db, tenant_id, invoice)
    pending_balance = invoice_total - other_payments
    _ensure_amount_within_balance(
        payment_update.amount,
        pending_balance,
        "Esta factura ya está totalmente pagada.",
    )

    db_payment.monto = payment_update.amount
    db_payment.fecha_pago = payment_update.payment_date
    db_payment.metodo_pago = payment_update.payment_method
    db_payment.nro_comprobante = payment_update.receipt_number
    db_payment.notas = payment_update.notes
    _update_invoice_status(
        invoice,
        other_payments + payment_update.amount,
        invoice_total,
    )

    record_audit_event(
        db,
        tenant_id,
        "updated",
        "purchase_payment",
        db_payment.id,
        before_data=before_data,
        after_data={
            **snapshot_fields(db_payment, _PAYMENT_AUDIT_FIELDS),
            "invoice_status": invoice.estado,
        },
    )
    db.commit()
    db.refresh(db_payment)
    return db_payment


def delete_payment(db: Session, tenant_id: int, payment_id: int):
    db_payment = (
        db.query(models.PurchasePayment)
        .filter(
            models.PurchasePayment.tenant_id == tenant_id,
            models.PurchasePayment.id == payment_id,
        )
        .first()
    )
    if not db_payment:
        raise HTTPException(status_code=404, detail="El pago no existe.")

    invoice = _get_locked_purchase_invoice(
        db, tenant_id, db_payment.factura_compra_id
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="La factura no existe.")

    before_data = {
        **snapshot_fields(db_payment, _PAYMENT_AUDIT_FIELDS),
        "invoice_status": invoice.estado,
    }
    db.delete(db_payment)
    db.flush()
    _update_invoice_status(
        invoice,
        _purchase_paid_total(db, tenant_id, invoice.id),
        _invoice_total(db, tenant_id, invoice),
    )
    record_audit_event(
        db,
        tenant_id,
        "deleted",
        "purchase_payment",
        db_payment.id,
        before_data=before_data,
        after_data={"invoice_status": invoice.estado},
    )
    db.commit()
    return {"detail": "Pago eliminado correctamente y estado de factura actualizado."}
