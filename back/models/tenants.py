from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class Tenant(Base):
    __tablename__ = "organizaciones"

    id = Column(Integer, primary_key=True, index=True)
    cuit = Column(String(11), unique=True, nullable=True)
    razon_social = Column(String, nullable=True)
    condicion_iva = Column(String) 
    domicilio = Column(String) 
    plan = Column(String(20), nullable=False, default="basico", server_default="basico") 
    usuarios = relationship("User", back_populates="organizacion", cascade="all, delete-orphan") 
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    empresas_asociadas = relationship("Company", back_populates="organizacion", cascade="all, delete-orphan")