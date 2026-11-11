from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class TenantBase(BaseModel):
    cuit: Optional[str] = Field(
        None,
        min_length=11,
        max_length=11,
        pattern=r"^\d{11}$",
        description="CUIT de 11 dígitos sin guiones",
    )
    razon_social: Optional[str] = Field(None, min_length=2, max_length=150)
    condicion_iva: Optional[str] = Field(None, max_length=50)
    domicilio: Optional[str] = Field(None, max_length=255)
class TenantCreate(TenantBase):
    pass


class TenantRegister(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    dni: Optional[str] = Field(None, min_length=7, max_length=8, pattern=r"^\d{7,8}$")
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
class TenantUpdate(BaseModel):
    cuit: Optional[str] = Field(None, min_length=11, max_length=11, pattern=r"^\d{11}$")
    razon_social: Optional[str] = Field(None, min_length=2, max_length=150)
    condicion_iva: Optional[str] = Field(None, max_length=50)
    domicilio: Optional[str] = Field(None, max_length=255)
class TenantResponse(TenantBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TenantRegisterResponse(BaseModel):
    tenant: TenantResponse
    user: dict
    message: str
    recovery_code: str
