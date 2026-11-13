# ==================================================
# SCRIPT DE SEED (DATOS DE EJEMPLO PARA EL FRONT)
# ==================================================
# Uso:  python -m back.seed   (desde la raíz del proyecto)
#
# Crea un tenant demo con:
#   - 2 usuarios (Admin y Marco)  -> clave: 789551
#   - 10 empresas (5 clientes + 5 proveedores)
#   - Facturas de venta + cobros para los clientes
#   - Facturas de compra + pagos para los proveedores
#
# Re-ejecutar BORRA los datos del tenant demo y los recarga
# desde cero (solo afecta a esa empresa demo, no al resto).

from datetime import date, timedelta
from decimal import Decimal
import secrets
from urllib.parse import urlparse

from database.database import SessionLocal
from database.config import settings
from database.security import get_password_hash
from back import models

# Datos fijos del seed
TENANT_CUIT = "30111111111"

CLIENTES = [
    ("Mercado Central SA", "20111111111"),
    ("Distribuidora Andina SRL", "20222222222"),
    ("Supermercados Norte SA", "20333333333"),
    ("Ferretería El Tornillo", "20444444444"),
    ("Clínica del Sol", "20555555555"),
]

PROVEEDORES = [
    ("Proveedora Industrial X SRL", "20666666666"),
    ("Mayorista de Insumos SA", "20777777777"),
    ("Logística Patagonia SRL", "20888888888"),
    ("Papelera del Sur SA", "20999999999"),
    ("Servicios Técnicos SRL", "20000000001"),
]


def _fecha_anterior(dias_antes: int) -> date:
    """Devuelve una fecha 'hace X días' (siempre reciente)."""
    return date.today() - timedelta(days=dias_antes)


def _fecha_previo_mes() -> date:
    """Devuelve un día del mes anterior (para el comparativo de crecimiento)."""
    hoy = date.today()
    ultimo_mes = hoy.replace(day=1) - timedelta(days=1)
    return ultimo_mes.replace(day=10)


def _validate_demo_seed_target(
    database_url: str,
    app_env: str,
    allow_demo_seed: bool,
) -> None:
    if not allow_demo_seed:
        raise RuntimeError(
            "Seed demo deshabilitado. Configura ALLOW_DEMO_SEED=true solo para desarrollo local."
        )
    if app_env.strip().lower() in {"prod", "production"}:
        raise RuntimeError("El seed demo no puede ejecutarse en producción.")

    parsed_url = urlparse(database_url)
    if parsed_url.scheme.startswith("sqlite"):
        return
    if parsed_url.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise RuntimeError("El seed demo solo puede ejecutarse contra una base local.")


def seed():
    _validate_demo_seed_target(
        settings.DATABASE_URL,
        settings.APP_ENV,
        settings.ALLOW_DEMO_SEED,
    )
    demo_password = secrets.token_urlsafe(18)
    db = SessionLocal()
    try:
        # ---------- 0. BORRADO DE DATOS ANTERIORES ----------
        # Re-ejecutar = recargar: borramos solo los datos del tenant demo
        # (empresas, usuarios, facturas, cobros, pagos) y los recreamos.
        existe = db.query(models.Tenant).filter(models.Tenant.cuit == TENANT_CUIT).first()
        if existe:
            tid = existe.id
            db.query(models.SalesCollection).filter_by(tenant_id=tid).delete()
            db.query(models.PurchasePayment).filter_by(tenant_id=tid).delete()
            db.query(models.SalesInvoice).filter_by(tenant_id=tid).delete()
            db.query(models.PurchaseInvoice).filter_by(tenant_id=tid).delete()
            db.query(models.Company).filter_by(tenant_id=tid).delete()
            db.query(models.User).filter_by(tenant_id=tid).delete()
            db.delete(existe)
            db.flush()
            print(f"Seed previo eliminado. Recargando datos demo...")

        # ---------- 1. TENANT ----------
        tenant = models.Tenant(
            cuit=TENANT_CUIT,
            razon_social="Empresa Demo SA",
            condicion_iva="Responsable Inscripto",
            domicilio="Av. Corrientes 1234, CABA",
        )
        db.add(tenant)
        db.flush()  # le asigna id sin commitear

        # ---------- 2. USUARIOS ----------
        # La clave se guarda SIEMPRE hasheada (bcrypt), nunca en texto plano.
        hash_clave = get_password_hash(demo_password)
        db.add_all([
            models.User(nombre="Admin", username="admin", email="admin@demo.com",
                        hashed_password=hash_clave, is_active=True, is_tenant_admin=True,
                        tenant_id=tenant.id),
            models.User(nombre="Marco", username="marco", email="marco@demo.com",
                        hashed_password=hash_clave, is_active=True, tenant_id=tenant.id),
        ])

        # ---------- 3. EMPRESAS (5 clientes + 5 proveedores) ----------
        clientes = {}
        for nombre, cuit in CLIENTES:
            c = models.Company(cuit=cuit, razon_social=nombre,
                               condicion_iva="Responsable Inscripto",
                               es_cliente=True, es_proveedor=False, tenant_id=tenant.id)
            db.add(c)
            clientes[nombre] = c

        proveedores = {}
        for nombre, cuit in PROVEEDORES:
            p = models.Company(cuit=cuit, razon_social=nombre,
                               condicion_iva="Monotributo",
                               es_cliente=False, es_proveedor=True, tenant_id=tenant.id)
            db.add(p)
            proveedores[nombre] = p

        db.flush()  # ahora todas las empresas tienen id

        # ---------- 4. FACTURAS DE VENTA + COBROS ----------
        # Estructura: (cliente, nro, monto, fecha_emision, fecha_pago_approx,
        #              estado_inicial, tipo, cobros[(monto, fecha)])
        # Los cobros SE APLICAN ANTES del commit para que el estado de cada
        # factura quede coherente (pagado/parcial) según lo cobrado.
        ventas = [
            # Emisión en MES ANTERIOR (para el comparativo de crecimiento):
            ("Mercado Central SA", 1, Decimal("1500000"), _fecha_previo_mes(), _fecha_anterior(45), "pendiente", "factura",
             [(Decimal("1500000"), _fecha_anterior(44))]),  # pagada
            ("Supermercados Norte SA", 5, Decimal("800000"), _fecha_previo_mes(), _fecha_anterior(30), "pendiente", "factura",
             [(Decimal("800000"), _fecha_anterior(29))]),  # pagada
            ("Clínica del Sol", 9, Decimal("350000"), _fecha_previo_mes(), _fecha_anterior(35), "pendiente", "factura",
             [(Decimal("350000"), _fecha_anterior(34))]),  # pagada
            # Emisión en ESTE MES (agosto):
            ("Mercado Central SA", 2, Decimal("900000"), _fecha_anterior(4), _fecha_anterior(-12), "pendiente", "factura",
             [(Decimal("400000"), _fecha_anterior(2))]),  # parcial, vence en 12 días
            ("Distribuidora Andina SRL", 3, Decimal("2300000"), _fecha_anterior(2), _fecha_anterior(-5), "pendiente", "factura",
             []),  # pendiente total, vence en 5 días
            ("Distribuidora Andina SRL", 4, Decimal("150000"), _fecha_anterior(2), _fecha_anterior(-20), "pendiente", "nota_credito",
             []),  # NC: resta del total
            ("Supermercados Norte SA", 6, Decimal("600000"), _fecha_anterior(3), _fecha_anterior(8), "pendiente", "factura",
             []),  # VENCIDA sin cobrar -> morosidad
            ("Ferretería El Tornillo", 7, Decimal("1100000"), _fecha_anterior(4), _fecha_anterior(-25), "pendiente", "factura",
             [(Decimal("500000"), _fecha_anterior(1))]),  # parcial, vence en 25 días
            ("Clínica del Sol", 8, Decimal("450000"), _fecha_anterior(2), _fecha_anterior(-40), "pendiente", "factura",
             []),  # pendiente, vence en 40 días
        ]

        for cliente, nro, monto, emision, vence, estado, tipo, cobros in ventas:
            factura = models.SalesInvoice(
                tenant_id=tenant.id,
                cliente_id=clientes[cliente].id,
                letra="A",
                punto_venta=1,
                nro_factura=nro,
                cae=f"CAE{nro:06d}",
                fecha_emision=emision,
                fecha_pago_approx=vence,
                monto_total=monto,
                estado=estado,
                tipo_comprobante=tipo,
                factura_origen_id=None,
            )
            db.add(factura)
            db.flush()

            # Aplicamos los cobros (como hace la API real: recalculan el estado)
            for monto_cobro, fecha_cobro in cobros:
                db.add(models.SalesCollection(
                    tenant_id=tenant.id,
                    factura_venta_id=factura.id,
                    monto=monto_cobro,
                    fecha_cobro=fecha_cobro,
                    metodo_cobro="Transferencia",
                ))

        # ---------- 5. FACTURAS DE COMPRA + PAGOS ----------
        # Igual lógica: (proveedor, nro, monto, emision, vencimiento, cobros->pagos)
        compras = [
            # MES ANTERIOR:
            ("Proveedora Industrial X SRL", 101, Decimal("700000"), _fecha_previo_mes(), _fecha_anterior(20), "pendiente", "factura",
             [(Decimal("700000"), _fecha_anterior(19))]),  # pagada
            ("Logística Patagonia SRL", 103, Decimal("500000"), _fecha_anterior(20), _fecha_anterior(1), "pendiente", "factura",
             []),  # VENCIDA sin pagar -> morosidad
            ("Papelera del Sur SA", 104, Decimal("900000"), _fecha_previo_mes(), _fecha_anterior(25), "pendiente", "factura",
             [(Decimal("900000"), _fecha_anterior(24))]),  # pagada
            # ESTE MES:
            ("Mayorista de Insumos SA", 102, Decimal("1200000"), _fecha_anterior(2), _fecha_anterior(-15), "pendiente", "factura",
             []),  # vence en 15 días
            ("Servicios Técnicos SRL", 105, Decimal("600000"), _fecha_anterior(3), _fecha_anterior(-30), "pendiente", "factura",
             [(Decimal("250000"), _fecha_anterior(1))]),  # parcial, vence en 30 días
        ]

        for proveedor, nro, monto, emision, vence, estado, tipo, pagos in compras:
            factura = models.PurchaseInvoice(
                tenant_id=tenant.id,
                proveedor_id=proveedores[proveedor].id,
                letra="A",
                punto_venta=2,
                nro_factura=nro,
                cae=f"CAE{nro:06d}",
                fecha_emision=emision,
                fecha_vencimiento=vence,
                monto_total=monto,
                moneda="ARS",
                estado=estado,
                tipo_comprobante=tipo,
                factura_origen_id=None,
            )
            db.add(factura)
            db.flush()

            for monto_pago, fecha_pago in pagos:
                db.add(models.PurchasePayment(
                    tenant_id=tenant.id,
                    factura_compra_id=factura.id,
                    monto=monto_pago,
                    fecha_pago=fecha_pago,
                    metodo_pago="Transferencia",
                ))

        # ---------- 6. RECALCULAMOS ESTADOS COMO LA API ----------
        # En vez de escribir el estado a mano, repetimos la lógica real:
        # pagado si lo cobrado >= total, parcial si > 0, pendiente si nada.
        for factura in db.query(models.SalesInvoice).filter_by(tenant_id=tenant.id):
            cobrado = sum(
                c.monto for c in db.query(models.SalesCollection)
                .filter_by(tenant_id=tenant.id, factura_venta_id=factura.id)
            )
            if cobrado >= factura.monto_total:
                factura.estado = "pagado"
            elif cobrado > 0:
                factura.estado = "parcial"

        for factura in db.query(models.PurchaseInvoice).filter_by(tenant_id=tenant.id):
            pagado = sum(
                p.monto for p in db.query(models.PurchasePayment)
                .filter_by(tenant_id=tenant.id, factura_compra_id=factura.id)
            )
            if pagado >= factura.monto_total:
                factura.estado = "pagado"
            elif pagado > 0:
                factura.estado = "parcial"

        db.commit()

        # ---------- 7. RESUMEN ----------
        print(f"SEED OK - tenant '{tenant.razon_social}' (id {tenant.id})")
        print(f"  usuarios: admin@demo.com y marco@demo.com (clave temporal: {demo_password})")
        print(f"  empresas: {db.query(models.Company).filter_by(tenant_id=tenant.id).count()}")
        print(f"  ventas:   {db.query(models.SalesInvoice).filter_by(tenant_id=tenant.id).count()} "
              f"+ {db.query(models.SalesCollection).filter_by(tenant_id=tenant.id).count()} cobros")
        print(f"  compras:  {db.query(models.PurchaseInvoice).filter_by(tenant_id=tenant.id).count()} "
              f"+ {db.query(models.PurchasePayment).filter_by(tenant_id=tenant.id).count()} pagos")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
