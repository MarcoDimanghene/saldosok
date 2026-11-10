from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


# =====================================================================
# 1. COBROS DE VENTAS (Sales Collections)
# =====================================================================
class CollectionBase(BaseModel):
    invoice_id: int                         # Mapea a 'factura_venta_id'
    amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)  # Mapea a 'monto'
    collection_date: date                   # Mapea a 'fecha_cobro'
    collection_method: Optional[str] = "Transferencia"  # Mapea a 'metodo_cobro'
    receipt_number: Optional[str] = None    # Mapea a 'nro_comprobante'
    notes: Optional[str] = None             # Mapea a 'notas'

class CollectionCreate(CollectionBase):
    pass

class CollectionResponse(BaseModel):
    id: int
    factura_venta_id: int
    monto: Decimal
    fecha_cobro: Optional[date] = None
    metodo_cobro: Optional[str] = None
    nro_comprobante: Optional[str] = None
    notas: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# 2. PAGOS DE COMPRAS (Purchase Payments)
# =====================================================================
class PaymentBase(BaseModel):
    invoice_id: int                         # Mapea a 'factura_compra_id'
    amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)  # Mapea a 'monto'
    payment_date: date                      # Mapea a 'fecha_pago'
    payment_method: Optional[str] = "Transferencia"  # Mapea a 'metodo_pago'
    receipt_number: Optional[str] = None    # Mapea a 'nro_comprobante'
    notes: Optional[str] = None             # Mapea a 'notas'

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(BaseModel):
    id: int
    factura_compra_id: int
    monto: Decimal
    fecha_pago: Optional[date] = None
    metodo_pago: Optional[str] = None
    nro_comprobante: Optional[str] = None
    notas: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)