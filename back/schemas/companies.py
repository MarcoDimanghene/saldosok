from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from typing import Optional

class CompanyBase(BaseModel):
    tax_id: Optional[str] = Field(None, min_length=11, max_length=11)
    legal_name: str
    tax_condition: Optional[str] = None
    condicion_fiscal: Optional[str] = None
    address: Optional[str] = None
    banco_principal: Optional[str] = None
    cbu_propio: Optional[str] = None
    alias_propio: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    banco: Optional[str] = None
    cbu_cvu: Optional[str] = None
    alias_cbu: Optional[str] = None
    titular_cuenta: Optional[str] = None
    categoria_servicio: Optional[str] = None
    dias_credito: int = Field(default=0, ge=0)
    contacto_nombre: Optional[str] = None
    email_1: Optional[str] = None
    email_2: Optional[str] = None
    telefono_1: Optional[str] = None
    telefono_2: Optional[str] = None
    observaciones: Optional[str] = None
    is_client: bool = False
    is_supplier: bool = False
    is_issuer: bool = False

    @model_validator(mode="after")
    def require_tax_id_unless_supplier_only(self):
        if not self.tax_id and not (
            self.is_supplier and not self.is_client and not self.is_issuer
        ):
            raise ValueError("El CUIT/CUIL es obligatorio salvo para proveedores.")
        return self

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    tax_id: Optional[str] = Field(None, min_length=11, max_length=11)
    legal_name: Optional[str] = None
    tax_condition: Optional[str] = None
    condicion_fiscal: Optional[str] = None
    address: Optional[str] = None
    banco_principal: Optional[str] = None
    cbu_propio: Optional[str] = None
    alias_propio: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    banco: Optional[str] = None
    cbu_cvu: Optional[str] = None
    alias_cbu: Optional[str] = None
    titular_cuenta: Optional[str] = None
    categoria_servicio: Optional[str] = None
    dias_credito: Optional[int] = Field(None, ge=0)
    contacto_nombre: Optional[str] = None
    email_1: Optional[str] = None
    email_2: Optional[str] = None
    telefono_1: Optional[str] = None
    telefono_2: Optional[str] = None
    observaciones: Optional[str] = None
    is_client: Optional[bool] = None
    is_supplier: Optional[bool] = None
    is_issuer: Optional[bool] = None

class CompanyResponse(BaseModel):
    id: int
    cuit: Optional[str] = None
    razon_social: str
    condicion_iva: Optional[str] = None
    condicion_fiscal: Optional[str] = None
    domicilio: Optional[str] = None
    banco_principal: Optional[str] = None
    cbu_propio: Optional[str] = None
    alias_propio: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    banco: Optional[str] = None
    cbu_cvu: Optional[str] = None
    alias_cbu: Optional[str] = None
    titular_cuenta: Optional[str] = None
    categoria_servicio: Optional[str] = None
    dias_credito: int = 0
    contacto_nombre: Optional[str] = None
    email_1: Optional[str] = None
    email_2: Optional[str] = None
    telefono_1: Optional[str] = None
    telefono_2: Optional[str] = None
    observaciones: Optional[str] = None
    es_cliente: bool = False
    es_proveedor: bool = False
    es_emisor: bool = False
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)