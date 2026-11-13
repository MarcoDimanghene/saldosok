from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional


# ==========================================
# SCHEMAS DE USUARIO
# ==========================================

# 1. Base común (Campos compartidos)
class UserBase(BaseModel):
    nombre: Optional[str] = None
    dni: Optional[str] = Field(None, min_length=7, max_length=8, pattern=r"^\d{7,8}$")
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True


# 2. Schema para invitar un nuevo usuario
class UserCreate(UserBase):
    email: EmailStr


# 3. Schema para Actualizar Usuario (Entrada opcional)
# Todos los campos son opcionales para permitir actualizaciones parciales (PATCH/PUT)
class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


# 4. Schema de Respuesta Pública (Salida)
# NUNCA devolvemos el hashed_password ni la clave plana por seguridad
class UserResponse(UserBase):
    id: int
    tenant_id: int
    is_tenant_admin: bool = False
    is_email_verified: bool = True

    # Configuración de Pydantic v2 para compatibilidad con modelos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(BaseModel):
    user: UserResponse
    message: str


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationToken(BaseModel):
    token: str


class EmailVerificationResponse(BaseModel):
    message: str
    recovery_code: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetToken(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=128)


class RecoveryCodePasswordReset(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    recovery_code: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)


# 5. Schema Interno (Uso exclusivo del servicio de Login/Auth)
# Incluye el hash para poder comparar la contraseña en el proceso de autenticación
class UserInDB(UserResponse):
    hashed_password: str