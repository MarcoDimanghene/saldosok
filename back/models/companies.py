from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class Company(Base):
    __tablename__ = "clientes"
    __table_args__ = (
        UniqueConstraint("tenant_id", "cuit", name="uq_clientes_tenant_cuit"),
    )

    id = Column(Integer, primary_key=True, index=True)
    cuit = Column(String(11), nullable=True)
    razon_social = Column(String, nullable=False)
    condicion_iva = Column(String) 
    banco_principal = Column(String)
    cbu_propio = Column(String)
    alias_propio = Column(String)
    domicilio = Column(String) 
    localidad = Column(String)
    provincia = Column(String)
    banco = Column(String)
    cbu_cvu = Column(String)
    alias_cbu = Column(String)
    titular_cuenta = Column(String)
    categoria_servicio = Column(String)
    dias_credito = Column(Integer, nullable=False, default=0, server_default="0")
    dias_cobro = Column(Integer, nullable=False, default=0, server_default="0")
    dias_pago = Column(Integer, nullable=False, default=0, server_default="0")
    contacto_nombre = Column(String)
    email_1 = Column(String)
    email_2 = Column(String)
    telefono_1 = Column(String)
    telefono_2 = Column(String)
    observaciones = Column(Text)
    es_cliente = Column(Boolean, default=False)
    es_proveedor = Column(Boolean, default=False)
    es_emisor = Column(Boolean, default=False, nullable=False, server_default="false")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    tenant_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    organizacion = relationship("Tenant", back_populates="empresas_asociadas")

    @property
    def condicion_fiscal(self):
        return self.condicion_iva