# ==================================================
# SCHEMAS DEL DASHBOARD
# ==================================================
# Estos modelos definen la FORMA exacta del JSON que devuelve
# el endpoint GET /dashboard/summary. FastAPI valida que la
# respuesta cumpla con esta estructura.

from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional


# ---------- 1. Contador por estado ----------
# Se usa para responder preguntas tipo:
# "¿Cuántas facturas de venta hay 'pagadas', 'parciales' y 'pendientes'?"
class StatusCount(BaseModel):
    estado: str          # Nombre del estado (ej: "pendiente", "parcial", "pagado")
    cantidad: int        # Cuántas facturas tienen ese estado
    monto: Decimal       # Suma del monto de esas facturas


# ---------- 2. Vencimientos por ventana de días ----------
# Representa "cuánto se cobra/cae en 7, 15 o 30 días"
class Bucket(BaseModel):
    dias: int            # Ventana en días (7, 15 o 30)
    cantidad: int        # Cantidad de facturas dentro de esa ventana
    monto: Decimal       # Monto acumulado de esas facturas


# ---------- 3. Cliente / Proveedor destacado ----------
# Para el "Top 5" del panel
class TopPartner(BaseModel):
    company_id: int      # Id de la empresa (tabla clientes)
    razon_social: str    # Nombre para mostrar
    monto: Decimal       # Monto facturado/comprado


# ---------- 4. Respuesta completa del dashboard ----------
class DashboardSummary(BaseModel):
    # --- Totales históricos del tenant ---
    total_sales: Decimal             # Suma de facturas de venta (NC resta)
    total_purchases: Decimal         # Suma de facturas de compra (NC resta)
    balance: Decimal                 # Ventas - Compras

    # --- Lo cobrado y lo pagado ---
    total_collected: Decimal         # Suma de todos los cobros
    total_paid: Decimal              # Suma de todos los pagos

    # --- Saldos pendientes (corazón de la conciliación) ---
    accounts_receivable: Decimal     # A cobrar = ventas - cobrado
    collection_rate: Optional[float] # % de cobrado sobre ventas
    accounts_payable: Decimal        # A pagar = compras - pagado
    payment_rate: Optional[float]    # % de pagado sobre compras

    # --- Facturas agrupadas por estado ---
    sales_by_status: List[StatusCount]
    purchases_by_status: List[StatusCount]

    # --- Próximos vencimientos (7/15/30 días) ---
    upcoming_collections: List[Bucket]   # Ventas por cobrar próximamente
    upcoming_payments: List[Bucket]      # Compras por pagar próximamente

    # --- Previsión de cobros por semana y mes ---
    collections_this_week: Decimal
    collections_next_week: Decimal
    collections_this_month: Decimal
    collections_next_month: Decimal

    # --- Vencidas sin cobrar / pagar (morosidad) ---
    overdue_sales_count: int
    overdue_sales_amount: Decimal
    overdue_purchases_count: int
    overdue_purchases_amount: Decimal

    # --- Comparación con el mes anterior ---
    sales_this_month: Decimal
    sales_prev_month: Decimal
    sales_growth: Optional[float]        # % de crecimiento (None si no hay base)
    purchases_this_month: Decimal
    purchases_prev_month: Decimal
    purchases_growth: Optional[float]

    # --- Top 5 clientes / proveedores ---
    top_clients: List[TopPartner]
    top_suppliers: List[TopPartner]
