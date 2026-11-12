from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

# =====================================================================
# 1. SCHEMA BASE COMÚN (Campos compartidos por compras y ventas)
# =====================================================================
class InvoiceBase(BaseModel):
    issuer_id: int
    receiver_id: int
    letter: str = Field(..., max_length=1)  # Ej: 'A', 'B', 'C'
    point_of_sale: int
    invoice_number: int
    cae: Optional[str] = None
    issue_date: date
    total_amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)


# =====================================================================
# 2. FACTURAS DE COMPRA (Purchase Invoices)
# =====================================================================
class PurchaseInvoiceCreate(InvoiceBase):
    receiver_id: Optional[int] = None
    due_date: Optional[date] = None
    currency: str = 'ARS'
    concept: Optional[str] = None
    # Nuevos campos opcionales:
    tipo_comprobante: Optional[str] = "factura"
    factura_origen_id: Optional[int] = None


class PurchasePendingCreate(BaseModel):
    supplier_id: int
    receiver_id: Optional[int] = None
    concept: str = Field(..., min_length=1, max_length=300)
    total_amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    due_date: Optional[date] = None
    currency: str = "ARS"


class PurchaseInvoiceComplete(BaseModel):
    letter: str = Field(..., min_length=1, max_length=1)
    point_of_sale: int = Field(..., ge=0)
    invoice_number: int = Field(..., gt=0)
    cae: Optional[str] = None
    issue_date: date
    due_date: Optional[date] = None
    total_amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    tipo_comprobante: str = "factura"

# Update (todos los campos opcionales para PATCH)
class PurchaseInvoiceUpdate(BaseModel):
    issuer_id: Optional[int] = None
    receiver_id: Optional[int] = None
    letter: Optional[str] = None
    point_of_sale: Optional[int] = None
    invoice_number: Optional[int] = None
    cae: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    total_amount: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)
    currency: Optional[str] = None
    concept: Optional[str] = Field(None, min_length=1, max_length=300)
    tipo_comprobante: Optional[str] = None
    factura_origen_id: Optional[int] = None

class PurchaseInvoiceResponse(BaseModel):
    id: int
    numero_interno: Optional[str] = None
    proveedor_id: int
    receptor_id: Optional[int] = None
    letra: Optional[str] = None
    punto_venta: Optional[int] = None
    nro_factura: Optional[int] = None
    cae: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    monto_total: Optional[Decimal] = None
    monto_pagado: Decimal = Decimal("0.00")
    moneda: Optional[str] = None
    estado: Optional[str] = None
    factura_recibida: bool = True
    concepto: Optional[str] = None
    tipo_comprobante: Optional[str] = None
    factura_origen_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# 3. FACTURAS DE VENTA (Sales Invoices)
# =====================================================================
class SalesInvoiceCreate(InvoiceBase):
    estimated_payment_date: date
    # Nuevos campos con valores por defecto:
    tipo_comprobante: Optional[str] = "factura"  # Si no mandan nada, asumimos que es factura
    factura_origen_id: Optional[int] = None      # Solo se usa si es NC o ND

# Update (todos los campos opcionales para PATCH)
class SalesInvoiceUpdate(BaseModel):
    issuer_id: Optional[int] = None
    receiver_id: Optional[int] = None
    letter: Optional[str] = None
    point_of_sale: Optional[int] = None
    invoice_number: Optional[int] = None
    cae: Optional[str] = None
    issue_date: Optional[date] = None
    estimated_payment_date: Optional[date] = None
    total_amount: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)
    tipo_comprobante: Optional[str] = None
    factura_origen_id: Optional[int] = None

class SalesInvoiceResponse(BaseModel):
    id: int
    emisor_id: Optional[int] = None
    cliente_id: int
    letra: Optional[str] = None
    punto_venta: Optional[int] = None
    nro_factura: Optional[int] = None
    cae: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_pago_approx: Optional[date] = None
    monto_total: Optional[Decimal] = None
    monto_cobrado: Decimal = Decimal("0.00")
    estado: Optional[str] = None
    tipo_comprobante: Optional[str] = None
    factura_origen_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
