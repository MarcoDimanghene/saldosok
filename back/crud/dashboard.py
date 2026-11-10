# ==================================================
# CRUD DEL DASHBOARD
# ==================================================
# Acá viven TODAS las consultas de agregados del panel.
# La regla de oro: cada consulta SIEMPRE filtra por tenant_id
# para que un usuario solo vea los datos de su organización.

from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_
from datetime import date, timedelta
from decimal import Decimal
from .. import models


# Expresión SQL: monto con signo según el tipo de comprobante
#  - "factura"      -> suma (+)         ej: $100
#  - "nota_credito" -> resta (-)         ej: -$20 (devolución)
#  - "nota_debito"  -> suma (+)          ej: $5 (recargo)
#  - NULL           -> suma (+)          datos viejos sin tipo cargado
def _monto_signed(modelo):
    return case(
        (modelo.tipo_comprobante == "nota_credito", -modelo.monto_total),
        else_=modelo.monto_total,
    )


# Helper para armar los buckets de vencimientos (7/15/30 días)
# Recibe la lista de (fecha, monto) y devuelve la suma por ventana.
def _armar_buckets(filas):
    hoy = date.today()
    buckets = []
    for dias in (7, 15, 30):
        limite = hoy + timedelta(days=dias)
        # Filtramos solo las facturas que caen dentro de esta ventana
        dentro = [m for f, m in filas if f and f <= limite]
        buckets.append({
            "dias": dias,
            "cantidad": len(dentro),
            "monto": Decimal(str(sum(dentro))).quantize(Decimal("0.01"))
            if dentro else Decimal("0.00"),
        })
    return buckets


def _obtener_saldos_por_fecha(
    db: Session,
    tenant_id: int,
    invoice_model,
    payment_model,
    payment_invoice_column,
    due_date_column,
    desde: date,
    hasta: date,
):
    pagos_por_factura = (
        db.query(
            payment_invoice_column.label("invoice_id"),
            func.sum(payment_model.monto).label("total_pagado"),
        )
        .filter(payment_model.tenant_id == tenant_id)
        .group_by(payment_invoice_column)
        .subquery()
    )
    saldo_pendiente = (
        func.coalesce(invoice_model.monto_total, 0)
        - func.coalesce(pagos_por_factura.c.total_pagado, 0)
    )

    return (
        db.query(due_date_column, saldo_pendiente)
        .outerjoin(
            pagos_por_factura,
            pagos_por_factura.c.invoice_id == invoice_model.id,
        )
        .filter(
            invoice_model.tenant_id == tenant_id,
            due_date_column >= desde,
            due_date_column <= hasta,
            saldo_pendiente > 0,
            or_(invoice_model.estado != "pagado", invoice_model.estado.is_(None)),
        )
        .all()
    )


def get_dashboard_summary(db: Session, tenant_id: int) -> dict:
    hoy = date.today()

    # ==================================================
    # 1. TOTALES DE VENTAS Y COMPRAS
    # ==================================================
    # SUM sobre el monto con signo; COALESCE(... ,0) para
    # que devuelva 0 en vez de NULL cuando no hay facturas.
    total_sales = db.query(
        func.coalesce(func.sum(_monto_signed(models.SalesInvoice)), 0)
    ).filter(models.SalesInvoice.tenant_id == tenant_id).scalar()

    total_purchases = db.query(
        func.coalesce(func.sum(_monto_signed(models.PurchaseInvoice)), 0)
    ).filter(models.PurchaseInvoice.tenant_id == tenant_id).scalar()

    # ==================================================
    # 2. LO COBRADO Y LO PAGADO (histórico)
    # ==================================================
    total_collected = db.query(
        func.coalesce(func.sum(models.SalesCollection.monto), 0)
    ).filter(models.SalesCollection.tenant_id == tenant_id).scalar()

    total_paid = db.query(
        func.coalesce(func.sum(models.PurchasePayment.monto), 0)
    ).filter(models.PurchasePayment.tenant_id == tenant_id).scalar()

    # ==================================================
    # 3. SALDOS PENDIENTES + PORCENTAJES
    # ==================================================
    accounts_receivable = Decimal(total_sales) - Decimal(total_collected)
    accounts_payable = Decimal(total_purchases) - Decimal(total_paid)

    # % de cobro: cobrado / ventas. Si no hay ventas, no tiene
    # sentido el porcentaje -> None (el frontend muestra "—").
    collection_rate = (
        round(Decimal(total_collected) / Decimal(total_sales) * 100, 1)
        if total_sales else None
    )
    payment_rate = (
        round(Decimal(total_paid) / Decimal(total_purchases) * 100, 1)
        if total_purchases else None
    )

    # ==================================================
    # 4. FACTURAS POR ESTADO (agrupación con GROUP BY)
    # ==================================================
    # SELECT estado, COUNT(*), SUM(monto) FROM facturas_venta
    # WHERE tenant_id = ? GROUP BY estado
    def _por_estado(modelo):
        filas = db.query(
            modelo.estado,
            func.count(modelo.id),
            func.coalesce(func.sum(modelo.monto_total), 0),
        ).filter(modelo.tenant_id == tenant_id).group_by(modelo.estado).all()
        return [
            {"estado": estado or "sin estado", "cantidad": cant, "monto": monto}
            for estado, cant, monto in filas
        ]

    sales_by_status = _por_estado(models.SalesInvoice)
    purchases_by_status = _por_estado(models.PurchaseInvoice)

    # ==================================================
    # 5. PRÓXIMOS VENCIMIENTOS (7/15/30 días)
    # ==================================================
    # Traemos todas las facturas a cobrar que vencen entre hoy
    # y 30 días y que todavía NO están pagadas. El cálculo por
    # ventana (7/15/30) se hace en Python con _armar_buckets().
    limite_30 = hoy + timedelta(days=30)

    filas_cobros = _obtener_saldos_por_fecha(
        db,
        tenant_id,
        models.SalesInvoice,
        models.SalesCollection,
        models.SalesCollection.factura_venta_id,
        models.SalesInvoice.fecha_pago_approx,
        hoy,
        limite_30,
    )
    filas_pagos = _obtener_saldos_por_fecha(
        db,
        tenant_id,
        models.PurchaseInvoice,
        models.PurchasePayment,
        models.PurchasePayment.factura_compra_id,
        models.PurchaseInvoice.fecha_vencimiento,
        hoy,
        limite_30,
    )

    upcoming_collections = _armar_buckets(filas_cobros)
    upcoming_payments = _armar_buckets(filas_pagos)

    # ==================================================
    # 6. PREVISIÓN DE COBROS POR SEMANA Y MES
    # ==================================================
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    inicio_semana_proxima = inicio_semana + timedelta(days=7)
    fin_semana_proxima = inicio_semana_proxima + timedelta(days=6)

    primer_dia_mes = hoy.replace(day=1)
    primer_dia_mes_proximo = (primer_dia_mes + timedelta(days=32)).replace(day=1)
    primer_dia_mes_siguiente = (
        primer_dia_mes_proximo + timedelta(days=32)
    ).replace(day=1)
    ultimo_dia_mes = primer_dia_mes_proximo - timedelta(days=1)
    ultimo_dia_mes_proximo = primer_dia_mes_siguiente - timedelta(days=1)

    filas_cobros_periodos = _obtener_saldos_por_fecha(
        db,
        tenant_id,
        models.SalesInvoice,
        models.SalesCollection,
        models.SalesCollection.factura_venta_id,
        models.SalesInvoice.fecha_pago_approx,
        min(inicio_semana, primer_dia_mes),
        max(fin_semana_proxima, ultimo_dia_mes_proximo),
    )

    def _suma_cobros_periodo(desde, hasta):
        return sum(
            (
                monto
                for fecha, monto in filas_cobros_periodos
                if desde <= fecha <= hasta
            ),
            Decimal("0.00"),
        )

    collections_this_week = _suma_cobros_periodo(inicio_semana, fin_semana)
    collections_next_week = _suma_cobros_periodo(
        inicio_semana_proxima, fin_semana_proxima
    )
    collections_this_month = _suma_cobros_periodo(primer_dia_mes, ultimo_dia_mes)
    collections_next_month = _suma_cobros_periodo(
        primer_dia_mes_proximo, ultimo_dia_mes_proximo
    )

    # ==================================================
    # 7. VENCIDAS SIN COBRAR / PAGAR (morosidad)
    # ==================================================
    # Las mismas cuentas que en el punto 5 pero con fecha ANTES de hoy.
    # OJO con el NULL: en SQL "NULL != 'pagado'" da NULL (no matchea),
    # por eso agregamos estado IS NULL con or_().
    overdue_sales = _obtener_saldos_por_fecha(
        db,
        tenant_id,
        models.SalesInvoice,
        models.SalesCollection,
        models.SalesCollection.factura_venta_id,
        models.SalesInvoice.fecha_pago_approx,
        date.min,
        hoy - timedelta(days=1),
    )
    overdue_purchases = _obtener_saldos_por_fecha(
        db,
        tenant_id,
        models.PurchaseInvoice,
        models.PurchasePayment,
        models.PurchasePayment.factura_compra_id,
        models.PurchaseInvoice.fecha_vencimiento,
        date.min,
        hoy - timedelta(days=1),
    )
    overdue_sales_count = len(overdue_sales)
    overdue_sales_amount = sum(
        (monto for _, monto in overdue_sales),
        Decimal("0.00"),
    )
    overdue_purchases_count = len(overdue_purchases)
    overdue_purchases_amount = sum(
        (monto for _, monto in overdue_purchases),
        Decimal("0.00"),
    )

    # ==================================================
    # 8. COMPARACIÓN CON EL MES ANTERIOR
    # ==================================================
    # Calculamos el primer día de este mes y el rango del mes pasado.
    primer_dia_mes = hoy.replace(day=1)
    ultimo_dia_anterior = primer_dia_mes - timedelta(days=1)
    primer_dia_anterior = ultimo_dia_anterior.replace(day=1)

    # Mismo SUM con signo pero filtrando por fecha de emisión.
    def _suma_periodo(modelo, desde, hasta):
        return db.query(
            func.coalesce(func.sum(_monto_signed(modelo)), 0)
        ).filter(
            modelo.tenant_id == tenant_id,
            modelo.fecha_emision >= desde,
            modelo.fecha_emision <= hasta,
        ).scalar()

    sales_this_month = _suma_periodo(models.SalesInvoice, primer_dia_mes, hoy)
    sales_prev_month = _suma_periodo(
        models.SalesInvoice, primer_dia_anterior, ultimo_dia_anterior
    )
    purchases_this_month = _suma_periodo(models.PurchaseInvoice, primer_dia_mes, hoy)
    purchases_prev_month = _suma_periodo(
        models.PurchaseInvoice, primer_dia_anterior, ultimo_dia_anterior
    )

    # Crecimiento porcentual: ((actual - anterior) / anterior) * 100
    # Si el mes anterior fue 0, no se puede calcular -> None.
    def _growth(actual, anterior):
        if anterior:
            return round(
                (Decimal(actual) - Decimal(anterior)) / Decimal(anterior) * 100, 1
            )
        return None

    sales_growth = _growth(sales_this_month, sales_prev_month)
    purchases_growth = _growth(purchases_this_month, purchases_prev_month)

    # ==================================================
    # 9. TOP 5 CLIENTES Y PROVEEDORES
    # ==================================================
    # JOIN entre facturas y la tabla de empresas para poder
    # mostrar el nombre junto al monto. Agrupamos por empresa
    # y ordenamos de mayor a menor.
    def _top(modelo_factura, columna_id):
        filas = db.query(
            columna_id,
            models.Company.razon_social,
            func.coalesce(func.sum(_monto_signed(modelo_factura)), 0),
        ).join(
            models.Company,
            (models.Company.id == columna_id)
            & (models.Company.tenant_id == tenant_id),
        ).filter(
            modelo_factura.tenant_id == tenant_id
        ).group_by(columna_id, models.Company.razon_social).all()

        # Ordenamos en Python y nos quedamos con las 5 primeras
        filas.sort(key=lambda f: f[2], reverse=True)
        return [
            {"company_id": cid, "razon_social": nombre, "monto": monto}
            for cid, nombre, monto in filas[:5]
        ]

    top_clients = _top(models.SalesInvoice, models.SalesInvoice.cliente_id)
    top_suppliers = _top(models.PurchaseInvoice, models.PurchaseInvoice.proveedor_id)

    # ==================================================
    # 10. ARMAMOS EL DICCIONARIO FINAL (lo valida el schema)
    # ==================================================
    return {
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "balance": Decimal(total_sales) - Decimal(total_purchases),
        "total_collected": total_collected,
        "total_paid": total_paid,
        "accounts_receivable": accounts_receivable,
        "collection_rate": collection_rate,
        "accounts_payable": accounts_payable,
        "payment_rate": payment_rate,
        "sales_by_status": sales_by_status,
        "purchases_by_status": purchases_by_status,
        "upcoming_collections": upcoming_collections,
        "upcoming_payments": upcoming_payments,
        "collections_this_week": collections_this_week,
        "collections_next_week": collections_next_week,
        "collections_this_month": collections_this_month,
        "collections_next_month": collections_next_month,
        "overdue_sales_count": overdue_sales_count,
        "overdue_sales_amount": overdue_sales_amount,
        "overdue_purchases_count": overdue_purchases_count,
        "overdue_purchases_amount": overdue_purchases_amount,
        "sales_this_month": sales_this_month,
        "sales_prev_month": sales_prev_month,
        "sales_growth": sales_growth,
        "purchases_this_month": purchases_this_month,
        "purchases_prev_month": purchases_prev_month,
        "purchases_growth": purchases_growth,
        "top_clients": top_clients,
        "top_suppliers": top_suppliers,
    }
