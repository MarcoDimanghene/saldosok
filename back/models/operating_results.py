from sqlalchemy import Column, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from database.database import Base


class OperatingResult(Base):
    __tablename__ = "resultados_operativos"
    __table_args__ = (
        UniqueConstraint("factura_compra_id", name="uq_ro_factura_compra"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    factura_compra_id = Column(
        Integer,
        ForeignKey("facturas_compra.id"),
        nullable=False,
    )
    monto_venta = Column(Numeric(15, 2), nullable=False)

    organizacion = relationship("Tenant")
    factura = relationship("PurchaseInvoice", back_populates="resultado_operativo")
