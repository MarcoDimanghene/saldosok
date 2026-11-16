from decimal import Decimal
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class OperatingResultCreate(BaseModel):
    factura_compra_id: int = Field(..., gt=0)
    monto_venta: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)


class OperatingResultUpdate(BaseModel):
    monto_venta: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)


class OperatingResultResponse(BaseModel):
    id: Optional[int] = None
    factura_compra_id: int
    numero_interno: Optional[str] = None
    proveedor: str
    letra: Optional[str] = None
    punto_venta: Optional[int] = None
    nro_factura: Optional[int] = None
    fecha_emision: Optional[date] = None
    monto_compra: Decimal
    monto_venta: Optional[Decimal] = None
    ganancia: Optional[Decimal] = None
    porcentaje_venta: Optional[Decimal] = None
    moneda: str = "ARS"
    model_config = {"from_attributes": True}
