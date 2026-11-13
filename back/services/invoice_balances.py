from decimal import Decimal

from sqlalchemy.orm import Session


def get_adjusted_invoice_totals(
    db: Session,
    tenant_id: int,
    invoice_model,
) -> dict[int, Decimal]:
    invoices = (
        db.query(
            invoice_model.id,
            invoice_model.factura_origen_id,
            invoice_model.tipo_comprobante,
            invoice_model.monto_total,
        )
        .filter(invoice_model.tenant_id == tenant_id)
        .all()
    )
    children: dict[int, list] = {}
    invoice_data = {}
    for invoice_id, origin_id, invoice_type, amount in invoices:
        invoice_data[invoice_id] = (
            invoice_type or "factura",
            Decimal(amount or 0),
        )
        if origin_id is not None:
            children.setdefault(origin_id, []).append(invoice_id)

    def adjustments_for(invoice_id: int, ancestors: frozenset[int]) -> Decimal:
        if invoice_id in ancestors:
            return Decimal("0.00")
        descendants = ancestors | {invoice_id}
        adjustment = Decimal("0.00")
        for child_id in children.get(invoice_id, []):
            child_type, amount = invoice_data[child_id]
            adjustment += -amount if child_type == "nota_credito" else amount
            adjustment += adjustments_for(child_id, descendants)
        return adjustment

    return {
        invoice_id: amount + adjustments_for(invoice_id, frozenset())
        for invoice_id, (_, amount) in invoice_data.items()
    }


def get_adjusted_invoice_total(
    db: Session,
    tenant_id: int,
    invoice,
) -> Decimal:
    totals = get_adjusted_invoice_totals(db, tenant_id, type(invoice))
    return totals.get(invoice.id, Decimal(invoice.monto_total or 0))


def attach_adjusted_invoice_totals(
    db: Session,
    tenant_id: int,
    invoices: list,
) -> list:
    if not invoices:
        return invoices
    invoice_model = type(invoices[0])
    totals = get_adjusted_invoice_totals(db, tenant_id, invoice_model)
    for invoice in invoices:
        invoice.monto_ajustado = (
            totals.get(invoice.id, Decimal(invoice.monto_total or 0))
            if (invoice.tipo_comprobante or "factura") == "factura"
            else None
        )
    return invoices
