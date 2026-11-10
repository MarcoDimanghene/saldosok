from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

# ==========================================
# 1. TABLA FACTURAS DE COMPRA
# ==========================================
class PurchaseInvoice(Base):
    __tablename__ = "facturas_compra"
    __table_args__ = (
        UniqueConstraint("numero_interno", name="uq_facturas_compra_numero_interno"),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Aislamiento por Tenant (Tu organización)
    tenant_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    
    # Proveedor que emite la factura (Apuntamos a la tabla 'clientes')
    proveedor_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    letra = Column(String(1))
    punto_venta = Column(Integer)
    nro_factura = Column(Integer)
    cae = Column(String)
    fecha_emision = Column(Date)
    fecha_vencimiento = Column(Date)
    monto_total = Column(Numeric(15, 2))
    moneda = Column(String, default="ARS")
    estado = Column(String, default="pendiente")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    numero_interno = Column(String, nullable=True)
    factura_recibida = Column(Boolean, default=True, nullable=False, server_default="true")
    concepto = Column(Text)

    # Notas de Crédito / Débito
    tipo_comprobante = Column(String, default="factura")  # "factura", "nota_credito", "nota_debito"
    factura_origen_id = Column(Integer, ForeignKey("facturas_compra.id"), nullable=True)

    # Relaciones
    organizacion = relationship("Tenant")
    proveedor = relationship("Company")


# ==========================================
# 2. TABLA FACTURAS DE VENTA
# ==========================================
class SalesInvoice(Base):
    __tablename__ = "facturas_venta"

    id = Column(Integer, primary_key=True, index=True)
    
    # Aislamiento por Tenant (Tu organización que emite la venta)
    tenant_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    
    # Cliente que recibe la factura (Apuntamos a la tabla 'clientes')
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    emisor_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    
    letra = Column(String(1))
    punto_venta = Column(Integer)
    nro_factura = Column(Integer)
    cae = Column(String)
    fecha_emision = Column(Date)
    fecha_pago_approx = Column(Date)
    monto_total = Column(Numeric(15, 2))
    estado = Column(String, default="pendiente")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Notas de Crédito / Débito
    tipo_comprobante = Column(String, default="factura")  # "factura", "nota_credito", "nota_debito"
    factura_origen_id = Column(Integer, ForeignKey("facturas_venta.id"), nullable=True)

    # Relaciones
    organizacion = relationship("Tenant")
    cliente = relationship("Company", foreign_keys=[cliente_id])
    emisor = relationship("Company", foreign_keys=[emisor_id])