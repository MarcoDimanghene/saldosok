from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class User(Base):
    __tablename__ = "usuarios"
    __table_args__ = (UniqueConstraint("dni", name="uq_usuarios_dni"),)

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=True)
    dni = Column(String(8), nullable=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, nullable=False, default=True, server_default="true")
    is_tenant_admin = Column(Boolean, nullable=False, default=False, server_default="false")
    is_superadmin = Column(Boolean, nullable=False, default=False, server_default="false")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Clave foránea que une al usuario con su organización (tenant)
    tenant_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)

    # Relación inversa para acceder al objeto Tenant desde el Usuario (ej: usuario.organizacion)
    organizacion = relationship("Tenant", back_populates="usuarios")