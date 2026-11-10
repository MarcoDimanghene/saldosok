from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

# ==========================================
# 1. TABLA COBROS DE VENTAS
# ==========================================
class SalesCollection(Base):
    __tablename__ = "cobros_ventas"

    id = Column(Integer, primary_key=True, index=True)
    
    # Aislamiento directo por Tenant
    tenant_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    
    factura_venta_id = Column(Integer, ForeignKey("facturas_venta.id"), nullable=False)
    monto = Column(Numeric(15, 2), nullable=False)
    fecha_cobro = Column(Date, server_default=func.current_date())
    metodo_cobro = Column(String) # Ej: "Transferencia", "Cheque", "Efectivo"
    nro_comprobante = Column(String)
    notas = Column(Text)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    organizacion = relationship("Tenant")
    factura = relationship("SalesInvoice")


# ==========================================
# 2. TABLA PAGOS DE COMPRAS
# ==========================================
class PurchasePayment(Base):
    __tablename__ = "pagos_compras"

    id = Column(Integer, primary_key=True, index=True)
    
    # Aislamiento directo por Tenant
    tenant_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    
    factura_compra_id = Column(Integer, ForeignKey("facturas_compra.id"), nullable=False)
    monto = Column(Numeric(15, 2), nullable=False)
    fecha_pago = Column(Date, server_default=func.current_date())
    metodo_pago = Column(String) # Ej: "Transferencia", "Cheque", "Efectivo"
    nro_comprobante = Column(String)
    notas = Column(Text)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    organizacion = relationship("Tenant")
    factura = relationship("PurchaseInvoice")