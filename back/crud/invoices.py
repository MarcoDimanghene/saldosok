from fastapi import HTTPException
from sqlalchemy.orm import Session
from back import models, schemas
from sqlalchemy import cast, String, func


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
    return (
        db.query(models.SalesInvoice)
        .filter(models.SalesInvoice.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# Crear venta
def create_sales_invoice(db: Session, tenant_id: int, invoice: schemas.SalesInvoiceCreate):
    _require_tenant_company(
        db,
        tenant_id,
        invoice.receiver_id,
        require_client=True,
    )
    _require_tenant_company(db, tenant_id, invoice.issuer_id, require_issuer=True)
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
    collected = None
    if "total_amount" in send_data:
        collected = db.query(
            func.coalesce(func.sum(models.SalesCollection.monto), 0)
        ).filter(
            models.SalesCollection.tenant_id == tenant_id,
            models.SalesCollection.factura_venta_id == invoice_id,
        ).scalar()
        if send_data["total_amount"] < collected:
            raise HTTPException(
                status_code=400,
                detail="El importe no puede ser menor que los cobros ya registrados.",
            )

    for key, value in send_data.items():
        columna = MAPEO_VENTAS.get(key)
        if columna and hasattr(db_invoice, columna):
            setattr(db_invoice, columna, value)

    if collected is not None:
        if collected >= db_invoice.monto_total:
            db_invoice.estado = "pagado"
        elif collected > 0:
            db_invoice.estado = "parcial"
        else:
            db_invoice.estado = "pendiente"

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
    return (
        db.query(models.PurchaseInvoice)
        .filter(models.PurchaseInvoice.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# Crear compra
def create_purchase_invoice(db: Session, tenant_id: int, invoice: schemas.PurchaseInvoiceCreate):
    _require_tenant_company(
        db,
        tenant_id,
        invoice.issuer_id,
        require_supplier=True,
    )
    db_invoice = models.PurchaseInvoice(
        tenant_id=tenant_id,                      # Inyección directa del tenant
        proveedor_id=invoice.issuer_id,           # El emisor de la compra es el proveedor
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
    db_invoice = models.PurchaseInvoice(
        tenant_id=tenant_id,
        proveedor_id=purchase.supplier_id,
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
    db.commit()
    db.refresh(invoice)
    return invoice

# Mapeo de campos del schema (inglés) a las columnas de la DB (español) para compras
MAPEO_COMPRAS = {
    "issuer_id": "proveedor_id",
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

    update_data = invoice_update.model_dump(exclude_unset=True)
    if "issuer_id" in update_data:
        _require_tenant_company(
            db,
            tenant_id,
            update_data["issuer_id"],
            require_supplier=True,
        )
    if "total_amount" in update_data:
        paid = db.query(
            func.coalesce(func.sum(models.PurchasePayment.monto), 0)
        ).filter(
            models.PurchasePayment.tenant_id == tenant_id,
            models.PurchasePayment.factura_compra_id == invoice_id,
        ).scalar()
        if update_data["total_amount"] < paid:
            raise HTTPException(
                status_code=400,
                detail="El importe no puede ser menor que los pagos ya registrados.",
            )

    for key, value in update_data.items():
        columna = MAPEO_COMPRAS.get(key)
        if columna and hasattr(db_invoice, columna):
            setattr(db_invoice, columna, value)

    if "total_amount" in update_data:
        paid = db.query(
            func.coalesce(func.sum(models.PurchasePayment.monto), 0)
        ).filter(
            models.PurchasePayment.tenant_id == tenant_id,
            models.PurchasePayment.factura_compra_id == invoice_id,
        ).scalar()
        if paid >= db_invoice.monto_total:
            db_invoice.estado = "pagado"
        elif paid > 0:
            db_invoice.estado = "parcial"
        else:
            db_invoice.estado = "pendiente"

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