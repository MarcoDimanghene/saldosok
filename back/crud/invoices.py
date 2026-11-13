from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from back import models, schemas
from sqlalchemy import cast, String, func
from back.services.audit import record_audit_event, snapshot_fields
from back.services.invoice_balances import (
    attach_adjusted_invoice_totals,
    get_adjusted_invoice_total,
)

_SALES_AUDIT_FIELDS = (
    "emisor_id",
    "cliente_id",
    "letra",
    "punto_venta",
    "nro_factura",
    "cae",
    "fecha_emision",
    "fecha_pago_approx",
    "monto_total",
    "estado",
    "tipo_comprobante",
    "factura_origen_id",
)
_PURCHASE_AUDIT_FIELDS = (
    "proveedor_id",
    "receptor_id",
    "letra",
    "punto_venta",
    "nro_factura",
    "cae",
    "fecha_emision",
    "fecha_vencimiento",
    "monto_total",
    "moneda",
    "estado",
    "factura_recibida",
    "concepto",
    "tipo_comprobante",
    "factura_origen_id",
    "numero_interno",
)

def _require_tenant_company(
    db: Session,
    tenant_id: int,
    company_id: int,
    require_issuer: bool = False,
    require_client: bool = False,
    require_supplier: bool = False,
) -> None:
    company = (
        db.query(models.Company)
        .filter(
            models.Company.id == company_id,
            models.Company.tenant_id == tenant_id,
        )
        .first()
    )
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
    if require_issuer and not company.es_emisor:
        raise HTTPException(
            status_code=400,
            detail="La empresa seleccionada no está habilitada como emisora.",
        )
    if require_client and not company.es_cliente:
        raise HTTPException(status_code=400, detail="La empresa no está registrada como cliente.")
    if require_supplier and not company.es_proveedor:
        raise HTTPException(
            status_code=400,
            detail="La empresa no está registrada como proveedor.",
        )


def _assign_internal_number(db: Session, invoice: models.PurchaseInvoice, tenant_id: int):
    db.flush()
    invoice.numero_interno = f"COMP-{tenant_id}-{invoice.id:06d}"


def _validate_note_origin(
    db: Session,
    tenant_id: int,
    invoice_model,
    invoice_type: str | None,
    origin_id: int | None,
    issuer_id: int,
    receiver_id: int | None,
    currency: str | None = None,
    invoice_id: int | None = None,
):
    invoice_type = invoice_type or "factura"
    if invoice_type not in {"factura", "nota_credito", "nota_debito"}:
        raise HTTPException(status_code=400, detail="Tipo de comprobante no válido.")
    if invoice_type == "factura":
        if origin_id is not None:
            raise HTTPException(
                status_code=400,
                detail="Una factura no puede tener un comprobante de origen.",
            )
        return None
    if origin_id is None:
        raise HTTPException(
            status_code=400,
            detail="La nota debe estar vinculada a un comprobante de origen.",
        )

    origin = (
        db.query(invoice_model)
        .filter(
            invoice_model.tenant_id == tenant_id,
            invoice_model.id == origin_id,
        )
        .first()
    )
    if origin is None:
        raise HTTPException(status_code=404, detail="El comprobante de origen no existe.")
    if invoice_id is not None and origin.id == invoice_id:
        raise HTTPException(
            status_code=400,
            detail="Un comprobante no puede vincularse a sí mismo.",
        )

    origin_type = origin.tipo_comprobante or "factura"
    valid_origin_types = (
        {"factura"} if invoice_type == "nota_credito"
        else {"factura", "nota_credito"}
    )
    if origin_type not in valid_origin_types:
        raise HTTPException(
            status_code=400,
            detail="La nota debe vincularse a una factura o a una nota de crédito.",
        )

    if invoice_model is models.SalesInvoice:
        same_parties = (
            origin.emisor_id == issuer_id
            and origin.cliente_id == receiver_id
        )
    else:
        same_parties = (
            origin.proveedor_id == issuer_id
            and origin.receptor_id == receiver_id
        )
    if not same_parties:
        raise HTTPException(
            status_code=400,
            detail="El comprobante de origen debe pertenecer a las mismas empresas.",
        )
    if invoice_model is models.PurchaseInvoice and currency:
        origin_currency = (origin.moneda or "ARS").upper()
        if origin_currency != currency.upper():
            raise HTTPException(
                status_code=400,
                detail="La nota debe estar expresada en la moneda del comprobante de origen.",
            )

    while (origin.tipo_comprobante or "factura") != "factura":
        if origin.factura_origen_id is None:
            raise HTTPException(
                status_code=400,
                detail="La nota de origen no está vinculada a una factura.",
            )
        if invoice_id is not None and origin.factura_origen_id == invoice_id:
            raise HTTPException(
                status_code=400,
                detail="La nota no puede vincularse a uno de sus comprobantes dependientes.",
            )
        origin = (
            db.query(invoice_model)
            .filter(
                invoice_model.tenant_id == tenant_id,
                invoice_model.id == origin.factura_origen_id,
            )
            .first()
        )
        if origin is None:
            raise HTTPException(status_code=404, detail="La factura de origen no existe.")
    return origin


def _invoice_root(db: Session, tenant_id: int, invoice_model, invoice):
    current = invoice
    while (current.tipo_comprobante or "factura") != "factura":
        if current.factura_origen_id is None:
            return None
        current = (
            db.query(invoice_model)
            .filter(
                invoice_model.tenant_id == tenant_id,
                invoice_model.id == current.factura_origen_id,
            )
            .first()
        )
        if current is None:
            return None
    return current


def _refresh_invoice_status(db: Session, tenant_id: int, invoice_model, invoice_id: int):
    invoice = (
        db.query(invoice_model)
        .filter(
            invoice_model.tenant_id == tenant_id,
            invoice_model.id == invoice_id,
        )
        .first()
    )
    if invoice is None or (invoice.tipo_comprobante or "factura") != "factura":
        return

    if invoice_model is models.SalesInvoice:
        payment_model = models.SalesCollection
        payment_invoice_column = models.SalesCollection.factura_venta_id
    else:
        payment_model = models.PurchasePayment
        payment_invoice_column = models.PurchasePayment.factura_compra_id
    paid = db.query(func.coalesce(func.sum(payment_model.monto), 0)).filter(
        payment_model.tenant_id == tenant_id,
        payment_invoice_column == invoice.id,
    ).scalar()
    adjusted_total = get_adjusted_invoice_total(db, tenant_id, invoice)
    if paid >= adjusted_total:
        invoice.estado = "pagado"
    elif paid > 0:
        invoice.estado = "parcial"
    else:
        invoice.estado = "pendiente"


#============================
#     FACTURAS DE VENTAS
#============================

# Buscar por CAE (dentro de la misma organización)
def get_sales_invoice_by_cae(db: Session, tenant_id: int, cae: str):
    return (
        db.query(models.SalesInvoice)
        .filter(models.SalesInvoice.tenant_id == tenant_id, models.SalesInvoice.cae == cae)
        .first()
    )

# Buscar por ID
def get_sales_invoice(db: Session, tenant_id: int, invoice_id: int):
    return (
        db.query(models.SalesInvoice)
        .filter(models.SalesInvoice.tenant_id == tenant_id, models.SalesInvoice.id == invoice_id)
        .first()
    )

# Listar todas las ventas del tenant
def get_listsales_invoices(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    invoices = (
        db.query(models.SalesInvoice)
        .options(selectinload(models.SalesInvoice.cobros))
        .filter(models.SalesInvoice.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return attach_adjusted_invoice_totals(db, tenant_id, invoices)

# Crear venta
def create_sales_invoice(db: Session, tenant_id: int, invoice: schemas.SalesInvoiceCreate):
    _require_tenant_company(
        db,
        tenant_id,
        invoice.receiver_id,
        require_client=True,
    )
    _require_tenant_company(db, tenant_id, invoice.issuer_id, require_issuer=True)
    origin = _validate_note_origin(
        db,
        tenant_id,
        models.SalesInvoice,
        invoice.tipo_comprobante,
        invoice.factura_origen_id,
        invoice.issuer_id,
        invoice.receiver_id,
    )
    db_invoice = models.SalesInvoice(
        tenant_id=tenant_id,                      # Inyección directa del tenant de la sesión
        cliente_id=invoice.receiver_id,           # El receptor de la venta es el cliente
        emisor_id=invoice.issuer_id,
        letra=invoice.letter,
        punto_venta=invoice.point_of_sale,
        nro_factura=invoice.invoice_number,
        cae=invoice.cae,
        fecha_emision=invoice.issue_date,
        fecha_pago_approx=invoice.estimated_payment_date,
        monto_total=invoice.total_amount,
        estado="pendiente",
        tipo_comprobante=invoice.tipo_comprobante,
        factura_origen_id=invoice.factura_origen_id
    )
    db.add(db_invoice)
    db.flush()
    if origin is not None:
        root = _invoice_root(db, tenant_id, models.SalesInvoice, origin)
        if root is not None:
            _refresh_invoice_status(db, tenant_id, models.SalesInvoice, root.id)
    record_audit_event(
        db,
        tenant_id,
        "created",
        "sales_invoice",
        db_invoice.id,
        after_data=snapshot_fields(db_invoice, _SALES_AUDIT_FIELDS),
    )
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

# Mapeo de campos del schema (inglés) a las columnas de la DB (español) para ventas
MAPEO_VENTAS = {
    "issuer_id": "emisor_id",
    "receiver_id": "cliente_id",
    "letter": "letra",
    "point_of_sale": "punto_venta",
    "invoice_number": "nro_factura",
    "cae": "cae",
    "issue_date": "fecha_emision",
    "estimated_payment_date": "fecha_pago_approx",
    "total_amount": "monto_total",
    "tipo_comprobante": "tipo_comprobante",
    "factura_origen_id": "factura_origen_id",
}

# Editar venta
def update_sales_invoice(db: Session, tenant_id: int, invoice_id: int, invoice_update: schemas.SalesInvoiceUpdate):
    db_invoice = (
        db.query(models.SalesInvoice)
        .filter(models.SalesInvoice.tenant_id == tenant_id, models.SalesInvoice.id == invoice_id)
        .first()
    )
    if not db_invoice:
        return None

    before_data = snapshot_fields(db_invoice, _SALES_AUDIT_FIELDS)
    send_data = invoice_update.model_dump(exclude_unset=True)
    if "receiver_id" in send_data:
        _require_tenant_company(
            db,
            tenant_id,
            send_data["receiver_id"],
            require_client=True,
        )
    if "issuer_id" in send_data:
        _require_tenant_company(
            db,
            tenant_id,
            send_data["issuer_id"],
            require_issuer=True,
        )
    old_root = _invoice_root(db, tenant_id, models.SalesInvoice, db_invoice)
    issuer_id = send_data.get("issuer_id", db_invoice.emisor_id)
    receiver_id = send_data.get("receiver_id", db_invoice.cliente_id)
    invoice_type = send_data.get("tipo_comprobante", db_invoice.tipo_comprobante)
    origin_id = send_data.get("factura_origen_id", db_invoice.factura_origen_id)
    new_root = _validate_note_origin(
        db,
        tenant_id,
        models.SalesInvoice,
        invoice_type,
        origin_id,
        issuer_id,
        receiver_id,
        invoice_id=invoice_id,
    )
    collected = None
    if "total_amount" in send_data:
        collected = db.query(
            func.coalesce(func.sum(models.SalesCollection.monto), 0)
        ).filter(
            models.SalesCollection.tenant_id == tenant_id,
            models.SalesCollection.factura_venta_id == invoice_id,
        ).scalar()
        adjusted_total = get_adjusted_invoice_total(db, tenant_id, db_invoice)
        if (invoice_type or "factura") == "factura":
            adjusted_total += send_data["total_amount"] - db_invoice.monto_total
        if adjusted_total < collected:
            raise HTTPException(
                status_code=400,
                detail="El importe no puede ser menor que los cobros ya registrados.",
            )

    for key, value in send_data.items():
        columna = MAPEO_VENTAS.get(key)
        if columna and hasattr(db_invoice, columna):
            setattr(db_invoice, columna, value)

    affected_roots = {
        root.id for root in (old_root, new_root) if root is not None
    }
    if (db_invoice.tipo_comprobante or "factura") == "factura":
        affected_roots.add(db_invoice.id)
    for root_id in affected_roots:
        _refresh_invoice_status(db, tenant_id, models.SalesInvoice, root_id)

    record_audit_event(
        db,
        tenant_id,
        "updated",
        "sales_invoice",
        db_invoice.id,
        before_data=before_data,
        after_data=snapshot_fields(db_invoice, _SALES_AUDIT_FIELDS),
    )
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

# Búsqueda dinámica por terminación de número
def search_sales_invoices_by_number_end(db: Session, tenant_id: int, last_digits: str):
    return (
        db.query(models.SalesInvoice)
        .filter(
            models.SalesInvoice.tenant_id == tenant_id,
            cast(models.SalesInvoice.nro_factura, String).like(f"%{last_digits}")
        )
        .all()
    )


#============================
#     FACTURAS DE COMPRAS
#============================

# Buscar por CAE
def get_purchase_by_cae(db: Session, tenant_id: int, cae: str):
    return (
        db.query(models.PurchaseInvoice)
        .filter(models.PurchaseInvoice.tenant_id == tenant_id, models.PurchaseInvoice.cae == cae)
        .first()
    )

# Buscar por ID
def get_purchase_invoice(db: Session, tenant_id: int, invoice_id: int):
    return (
        db.query(models.PurchaseInvoice)
        .filter(models.PurchaseInvoice.tenant_id == tenant_id, models.PurchaseInvoice.id == invoice_id)
        .first()
    )

# Listar todas las compras del tenant
def get_listpurchase_invoice(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    invoices = (
        db.query(models.PurchaseInvoice)
        .options(selectinload(models.PurchaseInvoice.pagos))
        .filter(models.PurchaseInvoice.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return attach_adjusted_invoice_totals(db, tenant_id, invoices)

# Crear compra
def create_purchase_invoice(db: Session, tenant_id: int, invoice: schemas.PurchaseInvoiceCreate):
    _require_tenant_company(
        db,
        tenant_id,
        invoice.issuer_id,
        require_supplier=True,
    )
    if invoice.receiver_id is not None:
        _require_tenant_company(db, tenant_id, invoice.receiver_id)
    origin = _validate_note_origin(
        db,
        tenant_id,
        models.PurchaseInvoice,
        invoice.tipo_comprobante,
        invoice.factura_origen_id,
        invoice.issuer_id,
        invoice.receiver_id,
        invoice.currency,
    )
    db_invoice = models.PurchaseInvoice(
        tenant_id=tenant_id,                      # Inyección directa del tenant
        proveedor_id=invoice.issuer_id,           # El emisor de la compra es el proveedor
        receptor_id=invoice.receiver_id,
        letra=invoice.letter,
        punto_venta=invoice.point_of_sale,
        nro_factura=invoice.invoice_number,
        cae=invoice.cae,
        fecha_emision=invoice.issue_date,
        fecha_vencimiento=invoice.due_date,
        monto_total=invoice.total_amount,
        moneda=invoice.currency,
        estado="pendiente",
        factura_recibida=True,
        concepto=invoice.concept,
        tipo_comprobante=invoice.tipo_comprobante,
        factura_origen_id=invoice.factura_origen_id
    )
    db.add(db_invoice)
    _assign_internal_number(db, db_invoice, tenant_id)
    if origin is not None:
        root = _invoice_root(db, tenant_id, models.PurchaseInvoice, origin)
        if root is not None:
            _refresh_invoice_status(db, tenant_id, models.PurchaseInvoice, root.id)
    record_audit_event(
        db,
        tenant_id,
        "created",
        "purchase_invoice",
        db_invoice.id,
        after_data=snapshot_fields(db_invoice, _PURCHASE_AUDIT_FIELDS),
    )
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def create_pending_purchase(
    db: Session,
    tenant_id: int,
    purchase: schemas.PurchasePendingCreate,
):
    _require_tenant_company(
        db,
        tenant_id,
        purchase.supplier_id,
        require_supplier=True,
    )
    if purchase.receiver_id is not None:
        _require_tenant_company(db, tenant_id, purchase.receiver_id)
    db_invoice = models.PurchaseInvoice(
        tenant_id=tenant_id,
        proveedor_id=purchase.supplier_id,
        receptor_id=purchase.receiver_id,
        monto_total=purchase.total_amount,
        fecha_vencimiento=purchase.due_date,
        moneda=purchase.currency,
        estado="pendiente",
        factura_recibida=False,
        concepto=purchase.concept.strip(),
        tipo_comprobante="factura",
    )
    db.add(db_invoice)
    _assign_internal_number(db, db_invoice, tenant_id)
    record_audit_event(
        db,
        tenant_id,
        "created",
        "purchase_invoice",
        db_invoice.id,
        after_data=snapshot_fields(db_invoice, _PURCHASE_AUDIT_FIELDS),
    )
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def complete_pending_purchase(
    db: Session,
    tenant_id: int,
    invoice_id: int,
    data: schemas.PurchaseInvoiceComplete,
):
    invoice = get_purchase_invoice(db, tenant_id, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="La compra no existe.")
    if invoice.factura_recibida:
        raise HTTPException(
            status_code=409,
            detail="La factura formal ya fue registrada para esta compra.",
        )
    if data.cae and get_purchase_by_cae(db, tenant_id, data.cae):
        raise HTTPException(
            status_code=409,
            detail="El CAE ya está registrado en otra compra.",
        )
    paid_total = db.query(
        func.coalesce(func.sum(models.PurchasePayment.monto), 0)
    ).filter(
        models.PurchasePayment.tenant_id == tenant_id,
        models.PurchasePayment.factura_compra_id == invoice.id,
    ).scalar()
    if data.total_amount < paid_total:
        raise HTTPException(
            status_code=400,
            detail="El importe formal no puede ser menor que los pagos ya registrados.",
        )

    before_data = snapshot_fields(invoice, _PURCHASE_AUDIT_FIELDS)
    invoice.letra = data.letter
    invoice.punto_venta = data.point_of_sale
    invoice.nro_factura = data.invoice_number
    invoice.cae = data.cae
    invoice.fecha_emision = data.issue_date
    invoice.fecha_vencimiento = data.due_date
    invoice.monto_total = data.total_amount
    invoice.tipo_comprobante = data.tipo_comprobante
    invoice.factura_recibida = True
    if paid_total >= data.total_amount:
        invoice.estado = "pagado"
    elif paid_total > 0:
        invoice.estado = "parcial"
    else:
        invoice.estado = "pendiente"
    record_audit_event(
        db,
        tenant_id,
        "updated",
        "purchase_invoice",
        invoice.id,
        before_data=before_data,
        after_data=snapshot_fields(invoice, _PURCHASE_AUDIT_FIELDS),
    )
    db.commit()
    db.refresh(invoice)
    return invoice

# Mapeo de campos del schema (inglés) a las columnas de la DB (español) para compras
MAPEO_COMPRAS = {
    "issuer_id": "proveedor_id",
    "receiver_id": "receptor_id",
    "letter": "letra",
    "point_of_sale": "punto_venta",
    "invoice_number": "nro_factura",
    "cae": "cae",
    "issue_date": "fecha_emision",
    "due_date": "fecha_vencimiento",
    "total_amount": "monto_total",
    "currency": "moneda",
    "concept": "concepto",
    "tipo_comprobante": "tipo_comprobante",
    "factura_origen_id": "factura_origen_id",
}

# Editar compra
def update_purchase_invoice(db: Session, tenant_id: int, invoice_id: int, invoice_update: schemas.PurchaseInvoiceUpdate):
    db_invoice = (
        db.query(models.PurchaseInvoice)
        .filter(models.PurchaseInvoice.tenant_id == tenant_id, models.PurchaseInvoice.id == invoice_id)
        .first()
    )
    if not db_invoice:
        return None

    before_data = snapshot_fields(db_invoice, _PURCHASE_AUDIT_FIELDS)
    update_data = invoice_update.model_dump(exclude_unset=True)
    if "issuer_id" in update_data:
        _require_tenant_company(
            db,
            tenant_id,
            update_data["issuer_id"],
            require_supplier=True,
        )
    if update_data.get("receiver_id") is not None:
        _require_tenant_company(db, tenant_id, update_data["receiver_id"])
    old_root = _invoice_root(db, tenant_id, models.PurchaseInvoice, db_invoice)
    issuer_id = update_data.get("issuer_id", db_invoice.proveedor_id)
    receiver_id = update_data.get("receiver_id", db_invoice.receptor_id)
    invoice_type = update_data.get("tipo_comprobante", db_invoice.tipo_comprobante)
    origin_id = update_data.get("factura_origen_id", db_invoice.factura_origen_id)
    new_root = _validate_note_origin(
        db,
        tenant_id,
        models.PurchaseInvoice,
        invoice_type,
        origin_id,
        issuer_id,
        receiver_id,
        update_data.get("currency", db_invoice.moneda),
        invoice_id=invoice_id,
    )
    if "total_amount" in update_data:
        paid = db.query(
            func.coalesce(func.sum(models.PurchasePayment.monto), 0)
        ).filter(
            models.PurchasePayment.tenant_id == tenant_id,
            models.PurchasePayment.factura_compra_id == invoice_id,
        ).scalar()
        adjusted_total = get_adjusted_invoice_total(db, tenant_id, db_invoice)
        if (invoice_type or "factura") == "factura":
            adjusted_total += update_data["total_amount"] - db_invoice.monto_total
        if adjusted_total < paid:
            raise HTTPException(
                status_code=400,
                detail="El importe no puede ser menor que los pagos ya registrados.",
            )

    for key, value in update_data.items():
        columna = MAPEO_COMPRAS.get(key)
        if columna and hasattr(db_invoice, columna):
            setattr(db_invoice, columna, value)

    affected_roots = {
        root.id for root in (old_root, new_root) if root is not None
    }
    if (db_invoice.tipo_comprobante or "factura") == "factura":
        affected_roots.add(db_invoice.id)
    for root_id in affected_roots:
        _refresh_invoice_status(db, tenant_id, models.PurchaseInvoice, root_id)

    record_audit_event(
        db,
        tenant_id,
        "updated",
        "purchase_invoice",
        db_invoice.id,
        before_data=before_data,
        after_data=snapshot_fields(db_invoice, _PURCHASE_AUDIT_FIELDS),
    )
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

# Búsqueda por terminación de número
def search_purchase_invoices_by_number_end(db: Session, tenant_id: int, last_digits: str):
    return (
        db.query(models.PurchaseInvoice)
        .filter(
            models.PurchaseInvoice.tenant_id == tenant_id,
            cast(models.PurchaseInvoice.nro_factura, String).like(f"%{last_digits}")
        )
        .all()
    )