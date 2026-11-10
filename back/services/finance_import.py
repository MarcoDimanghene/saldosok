from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from back import models


MAX_IMPORT_ROWS = 5000


def _normalize_cuit(value) -> str:
    return re.sub(r"[\s-]", "", str(value or ""))


def _parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except (TypeError, ValueError):
        return None


def _parse_amount(value):
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        return None
    if not amount.is_finite() or amount <= 0:
        return None
    decimal_places = max(-amount.as_tuple().exponent, 0)
    whole_digits = max(amount.adjusted() + 1, 0)
    if decimal_places > 2 or whole_digits + decimal_places > 15:
        return None
    return amount


def _parse_integer(value, minimum=0):
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        return None
    if not number.is_finite() or number != number.to_integral_value():
        return None
    result = int(number)
    return result if result >= minimum else None


def _parse_boolean(value):
    if isinstance(value, bool):
        return value
    normalized = str(value or "").strip().casefold()
    if normalized in {"si", "sí", "true", "1"}:
        return True
    if normalized in {"no", "false", "0"}:
        return False
    return None


def _row_number(row, index):
    return row.get("rowNumber", index + 2)


def import_finance_rows(db: Session, tenant_id: int, payload) -> dict:
    rows_by_sheet = {
        "Empresas": payload.companies,
        "Ventas": payload.sales,
        "Compras": payload.purchases,
        "Cobros": payload.collections,
        "Pagos": payload.payments,
    }
    row_count = sum(len(rows) for rows in rows_by_sheet.values())
    if row_count > MAX_IMPORT_ROWS:
        return {
            "ok": False,
            "errors": [{
                "sheet": "Planilla",
                "row": None,
                "field": None,
                "message": f"El máximo permitido es de {MAX_IMPORT_ROWS} filas por importación.",
            }],
        }

    errors = []

    def add_error(sheet, row_number, field, message):
        errors.append({
            "sheet": sheet,
            "row": row_number,
            "field": field,
            "message": message,
        })

    tenant = (
        db.query(models.Tenant)
        .filter(models.Tenant.id == tenant_id)
        .with_for_update()
        .first()
    )
    if tenant is None:
        raise HTTPException(status_code=404, detail="La organización no existe.")

    companies = (
        db.query(models.Company)
        .filter(models.Company.tenant_id == tenant_id)
        .all()
    )
    companies_by_cuit = {_normalize_cuit(company.cuit): company for company in companies}
    companies_by_id = {company.id: company for company in companies}
    new_companies = []
    primary_issuer = next((company for company in companies if company.es_emisor), None)
    issuer_update = None
    issuer_row_seen = False

    for index, row in enumerate(rows_by_sheet["Empresas"]):
        sheet = "Empresas"
        row_number = _row_number(row, index)
        error_count = len(errors)
        cuit_value = row.get("cuit")
        cuit = _normalize_cuit(cuit_value) if cuit_value not in (None, "") else None
        if cuit and (len(cuit) != 11 or not cuit.isdigit()):
            add_error(sheet, row_number, "CUIT/CUIL", "Ingresá un CUIT/CUIL válido de 11 dígitos.")
        is_issuer = _parse_boolean(row.get("es_emisor"))
        if is_issuer is None:
            add_error(sheet, row_number, "Es emisor", "Ingresá Sí o No.")
        if is_issuer and issuer_row_seen:
            add_error(sheet, row_number, "Es emisor", "Solo puede haber una fila marcada como emisor.")
        if is_issuer:
            issuer_row_seen = True
        existing_company = companies_by_cuit.get(cuit) if cuit else None
        if cuit and cuit in companies_by_cuit and not (
            is_issuer and existing_company is primary_issuer
        ):
            add_error(sheet, row_number, "CUIT/CUIL", f"El CUIT/CUIL {cuit} ya está registrado en Empresas.")
        if is_issuer and cuit:
            other_tenant = (
                db.query(models.Tenant.id)
                .filter(models.Tenant.cuit == cuit, models.Tenant.id != tenant_id)
                .first()
            )
            if other_tenant:
                add_error(sheet, row_number, "CUIT/CUIL", "El CUIT ya está registrado en otra organización.")

        legal_name = str(row.get("razon_social") or "").strip()
        if not legal_name:
            add_error(sheet, row_number, "Razón social", "Ingresá una razón social.")
        elif len(legal_name) > 150:
            add_error(sheet, row_number, "Razón social", "No puede superar los 150 caracteres.")

        is_client = _parse_boolean(row.get("es_cliente"))
        is_supplier = _parse_boolean(row.get("es_proveedor"))
        if is_client is None:
            add_error(sheet, row_number, "Es cliente", "Ingresá Sí o No.")
        if is_supplier is None:
            add_error(sheet, row_number, "Es proveedor", "Ingresá Sí o No.")
        if is_client is False and is_supplier is False and is_issuer is False:
            add_error(sheet, row_number, "Rol", "Seleccioná al menos un rol: cliente, proveedor o emisor.")
        if not cuit and (is_client or not is_supplier or is_issuer):
            add_error(sheet, row_number, "CUIT/CUIL", "El CUIT/CUIL es obligatorio para clientes y emisores.")
        tax_condition = str(row.get("condicion_iva") or "").strip() or None
        address = str(row.get("domicilio") or "").strip() or None
        if is_issuer and tax_condition and len(tax_condition) > 50:
            add_error(sheet, row_number, "Condición de IVA", "No puede superar los 50 caracteres.")
        if is_issuer and address and len(address) > 255:
            add_error(sheet, row_number, "Domicilio", "No puede superar los 255 caracteres.")

        if len(errors) != error_count:
            continue

        if is_issuer:
            company = primary_issuer or models.Company(tenant_id=tenant_id)
            issuer_update = {
                "cuit": cuit,
                "razon_social": legal_name,
                "condicion_iva": tax_condition,
                "domicilio": address,
                "localidad": str(row.get("localidad") or "").strip() or None,
                "provincia": str(row.get("provincia") or "").strip() or None,
                "es_cliente": is_client,
                "es_proveedor": is_supplier,
                "es_emisor": True,
            }
            if primary_issuer is None:
                new_companies.append(company)
                primary_issuer = company
            else:
                old_cuit = _normalize_cuit(primary_issuer.cuit)
                if old_cuit:
                    companies_by_cuit.pop(old_cuit, None)
            if company in new_companies:
                for field, value in issuer_update.items():
                    setattr(company, field, value)
            companies_by_cuit[cuit] = company
        else:
            company = models.Company(
                cuit=cuit,
                razon_social=legal_name,
                condicion_iva=tax_condition,
                domicilio=address,
                localidad=str(row.get("localidad") or "").strip() or None,
                provincia=str(row.get("provincia") or "").strip() or None,
                es_cliente=is_client,
                es_proveedor=is_supplier,
                tenant_id=tenant_id,
            )
            new_companies.append(company)
            if cuit:
                companies_by_cuit[cuit] = company

    def get_company(cuit_value, sheet, row_number, field, required_role):
        cuit = _normalize_cuit(cuit_value)
        if len(cuit) != 11 or not cuit.isdigit():
            add_error(sheet, row_number, field, "Ingresá un CUIT válido de 11 dígitos.")
            return None
        company = companies_by_cuit.get(cuit)
        if company is None:
            add_error(
                sheet,
                row_number,
                field,
                f"El CUIT {cuit} no está registrado en Empresas.",
            )
            return None
        if not getattr(company, required_role):
            role_names = {
                "es_emisor": "emisor",
                "es_cliente": "cliente",
                "es_proveedor": "proveedor",
            }
            add_error(
                sheet,
                row_number,
                field,
                f"La empresa con CUIT {cuit} no está habilitada como {role_names[required_role]}.",
            )
            return None
        return company

    sales_by_key = {}
    purchases_by_key = {}

    for invoice in (
        db.query(models.SalesInvoice)
        .filter(models.SalesInvoice.tenant_id == tenant_id)
        .with_for_update()
        .all()
    ):
        issuer = companies_by_id.get(invoice.emisor_id)
        client = companies_by_id.get(invoice.cliente_id)
        if issuer and client and invoice.letra and invoice.punto_venta is not None and invoice.nro_factura is not None:
            key = (
                _normalize_cuit(issuer.cuit),
                _normalize_cuit(client.cuit),
                invoice.letra.upper(),
                invoice.punto_venta,
                invoice.nro_factura,
            )
            sales_by_key.setdefault(key, []).append(invoice)

    for invoice in (
        db.query(models.PurchaseInvoice)
        .filter(models.PurchaseInvoice.tenant_id == tenant_id)
        .with_for_update()
        .all()
    ):
        supplier = companies_by_id.get(invoice.proveedor_id)
        if supplier and invoice.letra and invoice.punto_venta is not None and invoice.nro_factura is not None:
            key = (
                _normalize_cuit(supplier.cuit),
                invoice.letra.upper(),
                invoice.punto_venta,
                invoice.nro_factura,
            )
            purchases_by_key.setdefault(key, []).append(invoice)

    existing_sales_caes = {
        cae for (cae,) in db.query(models.SalesInvoice.cae).filter(
            models.SalesInvoice.tenant_id == tenant_id,
            models.SalesInvoice.cae.isnot(None),
        ).all()
    }
    existing_purchase_caes = {
        cae for (cae,) in db.query(models.PurchaseInvoice.cae).filter(
            models.PurchaseInvoice.tenant_id == tenant_id,
            models.PurchaseInvoice.cae.isnot(None),
        ).all()
    }

    new_sales = []
    new_purchases = []
    seen_sales = set()
    seen_purchases = set()
    seen_sales_caes = set()
    seen_purchase_caes = set()

    for index, row in enumerate(rows_by_sheet["Ventas"]):
        sheet = "Ventas"
        row_number = _row_number(row, index)
        error_count = len(errors)
        issuer = get_company(row.get("cuit_emisor"), sheet, row_number, "CUIT emisor", "es_emisor")
        client = get_company(row.get("cuit_cliente"), sheet, row_number, "CUIT cliente", "es_cliente")
        letter = str(row.get("letra") or "").strip().upper()
        if len(letter) != 1:
            add_error(sheet, row_number, "Letra", "Ingresá una letra de comprobante.")
        point_of_sale = _parse_integer(row.get("punto_venta"))
        invoice_number = _parse_integer(row.get("numero_factura"), minimum=1)
        if point_of_sale is None:
            add_error(sheet, row_number, "Punto de venta", "Ingresá un número entero igual o mayor a cero.")
        if invoice_number is None:
            add_error(sheet, row_number, "Nro factura", "Ingresá un número entero mayor a cero.")
        issue_date = _parse_date(row.get("fecha_emision"))
        due_date = _parse_date(row.get("fecha_vencimiento"))
        if issue_date is None:
            add_error(sheet, row_number, "Fecha de emisión", "Ingresá una fecha válida (AAAA-MM-DD).")
        if due_date is None:
            add_error(sheet, row_number, "Fecha estimada de cobro", "Ingresá una fecha válida (AAAA-MM-DD).")
        amount = _parse_amount(row.get("importe"))
        if amount is None:
            add_error(sheet, row_number, "Importe", "Ingresá un importe positivo con hasta dos decimales.")
        cae = str(row.get("cae") or "").strip() or None

        if len(errors) != error_count:
            continue

        key = (
            _normalize_cuit(issuer.cuit),
            _normalize_cuit(client.cuit),
            letter,
            point_of_sale,
            invoice_number,
        )
        if key in seen_sales or key in sales_by_key:
            add_error(sheet, row_number, "Nro factura", "La factura de venta ya está registrada o repetida en la planilla.")
            continue
        if cae and (cae in existing_sales_caes or cae in seen_sales_caes):
            add_error(sheet, row_number, "CAE", "El CAE ya está registrado o repetido en la planilla.")
            continue

        invoice = models.SalesInvoice(
            tenant_id=tenant_id,
            emisor=issuer,
            cliente=client,
            letra=letter,
            punto_venta=point_of_sale,
            nro_factura=invoice_number,
            cae=cae,
            fecha_emision=issue_date,
            fecha_pago_approx=due_date,
            monto_total=amount,
            estado="pendiente",
            tipo_comprobante="factura",
        )
        new_sales.append(invoice)
        sales_by_key[key] = [invoice]
        seen_sales.add(key)
        if cae:
            seen_sales_caes.add(cae)

    for index, row in enumerate(rows_by_sheet["Compras"]):
        sheet = "Compras"
        row_number = _row_number(row, index)
        error_count = len(errors)
        supplier = get_company(
            row.get("cuit_proveedor"),
            sheet,
            row_number,
            "CUIT proveedor",
            "es_proveedor",
        )
        letter = str(row.get("letra") or "").strip().upper()
        if len(letter) != 1:
            add_error(sheet, row_number, "Letra", "Ingresá una letra de comprobante.")
        point_of_sale = _parse_integer(row.get("punto_venta"))
        invoice_number = _parse_integer(row.get("numero_factura"), minimum=1)
        if point_of_sale is None:
            add_error(sheet, row_number, "Punto de venta", "Ingresá un número entero igual o mayor a cero.")
        if invoice_number is None:
            add_error(sheet, row_number, "Nro factura", "Ingresá un número entero mayor a cero.")
        issue_date = _parse_date(row.get("fecha_emision"))
        if issue_date is None:
            add_error(sheet, row_number, "Fecha de emisión", "Ingresá una fecha válida (AAAA-MM-DD).")
        due_date_value = row.get("fecha_vencimiento")
        due_date = _parse_date(due_date_value) if due_date_value not in (None, "") else None
        if due_date_value not in (None, "") and due_date is None:
            add_error(sheet, row_number, "Fecha de vencimiento", "Ingresá una fecha válida (AAAA-MM-DD).")
        amount = _parse_amount(row.get("importe"))
        if amount is None:
            add_error(sheet, row_number, "Importe", "Ingresá un importe positivo con hasta dos decimales.")
        cae = str(row.get("cae") or "").strip() or None
        concept = str(row.get("concepto") or "").strip() or None
        currency = str(row.get("moneda") or "ARS").strip().upper()
        if len(currency) > 10:
            add_error(sheet, row_number, "Moneda", "La moneda no puede superar los 10 caracteres.")

        if len(errors) != error_count:
            continue

        key = (
            _normalize_cuit(supplier.cuit),
            letter,
            point_of_sale,
            invoice_number,
        )
        if key in seen_purchases or key in purchases_by_key:
            add_error(sheet, row_number, "Nro factura", "La factura de compra ya está registrada o repetida en la planilla.")
            continue
        if cae and (cae in existing_purchase_caes or cae in seen_purchase_caes):
            add_error(sheet, row_number, "CAE", "El CAE ya está registrado o repetido en la planilla.")
            continue

        invoice = models.PurchaseInvoice(
            tenant_id=tenant_id,
            proveedor=supplier,
            letra=letter,
            punto_venta=point_of_sale,
            nro_factura=invoice_number,
            cae=cae,
            fecha_emision=issue_date,
            fecha_vencimiento=due_date,
            monto_total=amount,
            moneda=currency,
            estado="pendiente",
            factura_recibida=True,
            concepto=concept,
            tipo_comprobante="factura",
        )
        new_purchases.append(invoice)
        purchases_by_key[key] = [invoice]
        seen_purchases.add(key)
        if cae:
            seen_purchase_caes.add(cae)

    sales_ids = [
        invoice.id for invoices in sales_by_key.values() for invoice in invoices if invoice.id
    ]
    purchase_ids = [
        invoice.id for invoices in purchases_by_key.values() for invoice in invoices if invoice.id
    ]
    sales_collected = {
        invoice_id: Decimal(amount)
        for invoice_id, amount in db.query(
            models.SalesCollection.factura_venta_id,
            func.coalesce(func.sum(models.SalesCollection.monto), 0),
        )
        .filter(
            models.SalesCollection.tenant_id == tenant_id,
            models.SalesCollection.factura_venta_id.in_(sales_ids),
        )
        .group_by(models.SalesCollection.factura_venta_id)
        .all()
    } if sales_ids else {}
    purchases_paid = {
        invoice_id: Decimal(amount)
        for invoice_id, amount in db.query(
            models.PurchasePayment.factura_compra_id,
            func.coalesce(func.sum(models.PurchasePayment.monto), 0),
        )
        .filter(
            models.PurchasePayment.tenant_id == tenant_id,
            models.PurchasePayment.factura_compra_id.in_(purchase_ids),
        )
        .group_by(models.PurchasePayment.factura_compra_id)
        .all()
    } if purchase_ids else {}
    existing_collection_receipts = {
        (invoice_id, movement.fecha_cobro, Decimal(movement.monto), movement.nro_comprobante)
        for invoice_id, movement in db.query(
            models.SalesCollection.factura_venta_id,
            models.SalesCollection,
        )
        .filter(
            models.SalesCollection.tenant_id == tenant_id,
            models.SalesCollection.factura_venta_id.in_(sales_ids),
            models.SalesCollection.nro_comprobante.isnot(None),
        )
        .all()
    } if sales_ids else set()
    existing_payment_receipts = {
        (invoice_id, movement.fecha_pago, Decimal(movement.monto), movement.nro_comprobante)
        for invoice_id, movement in db.query(
            models.PurchasePayment.factura_compra_id,
            models.PurchasePayment,
        )
        .filter(
            models.PurchasePayment.tenant_id == tenant_id,
            models.PurchasePayment.factura_compra_id.in_(purchase_ids),
            models.PurchasePayment.nro_comprobante.isnot(None),
        )
        .all()
    } if purchase_ids else set()

    collections_to_create = []
    payments_to_create = []
    seen_collections = set()
    seen_payments = set()
    imported_collections = {}
    imported_payments = {}

    def parse_settlement_rows(sheet, rows, invoice_map, is_collection):
        for index, row in enumerate(rows):
            row_number = _row_number(row, index)
            error_count = len(errors)
            if is_collection:
                issuer = get_company(row.get("cuit_emisor"), sheet, row_number, "CUIT emisor", "es_emisor")
                client = get_company(row.get("cuit_cliente"), sheet, row_number, "CUIT cliente", "es_cliente")
                key_prefix = (
                    _normalize_cuit(issuer.cuit) if issuer else "",
                    _normalize_cuit(client.cuit) if client else "",
                )
            else:
                supplier = get_company(
                    row.get("cuit_proveedor"),
                    sheet,
                    row_number,
                    "CUIT proveedor",
                    "es_proveedor",
                )
                key_prefix = (_normalize_cuit(supplier.cuit) if supplier else "",)

            letter = str(row.get("letra") or "").strip().upper()
            if len(letter) != 1:
                add_error(sheet, row_number, "Letra", "Ingresá una letra de comprobante.")
            point_of_sale = _parse_integer(row.get("punto_venta"))
            invoice_number = _parse_integer(row.get("numero_factura"), minimum=1)
            if point_of_sale is None:
                add_error(sheet, row_number, "Punto de venta", "Ingresá un número entero igual o mayor a cero.")
            if invoice_number is None:
                add_error(sheet, row_number, "Nro factura", "Ingresá un número entero mayor a cero.")
            movement_date = _parse_date(row.get("fecha"))
            if movement_date is None:
                add_error(sheet, row_number, "Fecha", "Ingresá una fecha válida (AAAA-MM-DD).")
            amount = _parse_amount(row.get("importe"))
            if amount is None:
                add_error(sheet, row_number, "Importe", "Ingresá un importe positivo con hasta dos decimales.")
            if len(errors) != error_count:
                continue

            key = (*key_prefix, letter, point_of_sale, invoice_number)
            matches = invoice_map.get(key, [])
            if not matches:
                invoice_label = "venta" if is_collection else "compra"
                add_error(
                    sheet,
                    row_number,
                    "Nro factura",
                    f"No se encontró la factura de {invoice_label} indicada.",
                )
                continue
            if len(matches) != 1:
                add_error(sheet, row_number, "Nro factura", "La referencia de factura no es única.")
                continue

            invoice = matches[0]
            invoice_id = invoice.id
            if is_collection:
                existing_amount = (
                    sales_collected.get(invoice_id, Decimal("0.00"))
                    if invoice_id is not None
                    else Decimal("0.00")
                )
                previous_amount = existing_amount + imported_collections.get(
                    invoice,
                    Decimal("0.00"),
                )
                balance = Decimal(invoice.monto_total or 0) - previous_amount
                if amount > balance:
                    add_error(
                        sheet,
                        row_number,
                        "Importe",
                        f"El cobro supera el saldo pendiente de ${balance}.",
                    )
                    continue
                receipt = str(row.get("comprobante") or "").strip() or None
                duplicate_key = (
                    invoice_id if invoice_id is not None else invoice,
                    movement_date,
                    amount,
                    receipt,
                )
                if receipt and (
                    duplicate_key in seen_collections
                    or duplicate_key in existing_collection_receipts
                ):
                    add_error(sheet, row_number, "Comprobante", "El cobro está repetido en la planilla.")
                    continue
                movement = models.SalesCollection(
                    tenant_id=tenant_id,
                    factura_venta_id=invoice_id,
                    monto=amount,
                    fecha_cobro=movement_date,
                    metodo_cobro=str(row.get("medio") or "Transferencia").strip() or "Transferencia",
                    nro_comprobante=receipt,
                    notas=str(row.get("notas") or "").strip() or None,
                )
                collections_to_create.append((invoice, movement))
                imported_collections[invoice] = previous_amount + amount
                if receipt:
                    seen_collections.add(duplicate_key)
            else:
                existing_amount = (
                    purchases_paid.get(invoice_id, Decimal("0.00"))
                    if invoice_id is not None
                    else Decimal("0.00")
                )
                previous_amount = existing_amount + imported_payments.get(
                    invoice,
                    Decimal("0.00"),
                )
                balance = Decimal(invoice.monto_total or 0) - previous_amount
                if amount > balance:
                    add_error(
                        sheet,
                        row_number,
                        "Importe",
                        f"El pago supera el saldo pendiente de ${balance}.",
                    )
                    continue
                receipt = str(row.get("comprobante") or "").strip() or None
                duplicate_key = (
                    invoice_id if invoice_id is not None else invoice,
                    movement_date,
                    amount,
                    receipt,
                )
                if receipt and (
                    duplicate_key in seen_payments
                    or duplicate_key in existing_payment_receipts
                ):
                    add_error(sheet, row_number, "Comprobante", "El pago está repetido en la planilla.")
                    continue
                movement = models.PurchasePayment(
                    tenant_id=tenant_id,
                    factura_compra_id=invoice_id,
                    monto=amount,
                    fecha_pago=movement_date,
                    metodo_pago=str(row.get("medio") or "Transferencia").strip() or "Transferencia",
                    nro_comprobante=receipt,
                    notas=str(row.get("notas") or "").strip() or None,
                )
                payments_to_create.append((invoice, movement))
                imported_payments[invoice] = previous_amount + amount
                if receipt:
                    seen_payments.add(duplicate_key)

    parse_settlement_rows("Cobros", rows_by_sheet["Cobros"], sales_by_key, True)
    parse_settlement_rows("Pagos", rows_by_sheet["Pagos"], purchases_by_key, False)

    if errors:
        return {"ok": False, "errors": errors}

    try:
        if issuer_update:
            tenant.cuit = issuer_update["cuit"]
            tenant.razon_social = issuer_update["razon_social"]
            tenant.condicion_iva = issuer_update["condicion_iva"]
            tenant.domicilio = issuer_update["domicilio"]
            if primary_issuer not in new_companies:
                for field, value in issuer_update.items():
                    setattr(primary_issuer, field, value)
        db.add_all(new_companies + new_sales + new_purchases)
        db.flush()
        for invoice in new_purchases:
            invoice.numero_interno = f"COMP-{tenant_id}-{invoice.id:06d}"

        for invoice, collection in collections_to_create:
            collection.factura_venta_id = invoice.id
            db.add(collection)
        for invoice, payment in payments_to_create:
            payment.factura_compra_id = invoice.id
            db.add(payment)

        for invoice, total in imported_collections.items():
            _update_invoice_status(invoice, total)
        for invoice, total in imported_payments.items():
            _update_invoice_status(invoice, total)

        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return {
        "ok": True,
        "imported": {
            "companies": len(new_companies),
            "issuer_updated": issuer_update is not None,
            "sales": len(new_sales),
            "purchases": len(new_purchases),
            "collections": len(collections_to_create),
            "payments": len(payments_to_create),
        },
    }


def _update_invoice_status(invoice, amount_settled: Decimal) -> None:
    total = Decimal(invoice.monto_total or 0)
    if amount_settled >= total:
        invoice.estado = "pagado"
    elif amount_settled > 0:
        invoice.estado = "parcial"
    else:
        invoice.estado = "pendiente"
