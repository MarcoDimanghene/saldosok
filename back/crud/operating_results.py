from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from back import models, schemas
from back.services.invoice_balances import get_adjusted_invoice_totals


def _result_response(invoice, supplier, result, adjusted_totals):
    cost = adjusted_totals.get(
        invoice.id,
        Decimal(invoice.monto_total or 0),
    )
    sale = Decimal(result.monto_venta) if result is not None else None
    profit = sale - cost if sale is not None else None
    percentage = (
        (profit / sale * Decimal("100")).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if sale
        else None
    )
    return schemas.OperatingResultResponse(
        id=result.id if result is not None else None,
        factura_compra_id=invoice.id,
        numero_interno=invoice.numero_interno,
        proveedor=supplier.razon_social,
        letra=invoice.letra,
        punto_venta=invoice.punto_venta,
        nro_factura=invoice.nro_factura,
        fecha_emision=invoice.fecha_emision,
        monto_compra=cost,
        monto_venta=sale,
        ganancia=profit,
        porcentaje_venta=percentage,
        moneda=invoice.moneda or "ARS",
    )


def list_operating_results(db: Session, tenant_id: int):
    rows = (
        db.query(
            models.PurchaseInvoice,
            models.Company,
            models.OperatingResult,
        )
        .join(
            models.Company,
            models.Company.id == models.PurchaseInvoice.proveedor_id,
        )
        .outerjoin(
            models.OperatingResult,
            (models.OperatingResult.factura_compra_id == models.PurchaseInvoice.id)
            & (models.OperatingResult.tenant_id == tenant_id),
        )
        .filter(
            models.PurchaseInvoice.tenant_id == tenant_id,
            models.PurchaseInvoice.factura_recibida.is_(True),
            models.PurchaseInvoice.tipo_comprobante == "factura",
        )
        .order_by(
            models.PurchaseInvoice.fecha_emision.desc(),
            models.PurchaseInvoice.id.desc(),
        )
        .all()
    )
    adjusted_totals = get_adjusted_invoice_totals(
        db,
        tenant_id,
        models.PurchaseInvoice,
    )
    return [
        _result_response(invoice, supplier, result, adjusted_totals)
        for invoice, supplier, result in rows
    ]


def _get_eligible_invoice(db: Session, tenant_id: int, invoice_id: int):
    invoice = (
        db.query(models.PurchaseInvoice)
        .filter(
            models.PurchaseInvoice.id == invoice_id,
            models.PurchaseInvoice.tenant_id == tenant_id,
            models.PurchaseInvoice.factura_recibida.is_(True),
            models.PurchaseInvoice.tipo_comprobante == "factura",
        )
        .first()
    )
    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró una factura de compra formal para el RO.",
        )
    return invoice


def create_operating_result(
    db: Session,
    tenant_id: int,
    data: schemas.OperatingResultCreate,
):
    invoice = _get_eligible_invoice(db, tenant_id, data.factura_compra_id)
    existing = (
        db.query(models.OperatingResult)
        .filter(models.OperatingResult.factura_compra_id == invoice.id)
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="La factura ya tiene un Resultado Operativo.",
        )

    result = models.OperatingResult(
        tenant_id=tenant_id,
        factura_compra_id=invoice.id,
        monto_venta=data.monto_venta,
    )
    db.add(result)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="La factura ya tiene un Resultado Operativo.",
        ) from error
    db.refresh(result)
    adjusted_totals = get_adjusted_invoice_totals(
        db,
        tenant_id,
        models.PurchaseInvoice,
    )
    return _result_response(
        invoice,
        invoice.proveedor,
        result,
        adjusted_totals,
    )


def update_operating_result(
    db: Session,
    tenant_id: int,
    result_id: int,
    data: schemas.OperatingResultUpdate,
):
    result = (
        db.query(models.OperatingResult)
        .filter(
            models.OperatingResult.id == result_id,
            models.OperatingResult.tenant_id == tenant_id,
        )
        .first()
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="El Resultado Operativo no existe.",
        )

    result.monto_venta = data.monto_venta
    db.commit()
    db.refresh(result)
    invoice = result.factura
    adjusted_totals = get_adjusted_invoice_totals(
        db,
        tenant_id,
        models.PurchaseInvoice,
    )
    return _result_response(
        invoice,
        invoice.proveedor,
        result,
        adjusted_totals,
    )
