from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database.config import settings
from database.database import get_db
# Importamos la clase User directamente
from back.models.user import User

# Configuración de Hasheo de contraseñas con Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Le indica a FastAPI/Swagger dónde estará el endpoint para pedir el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_password_hash(password: str) -> str:
    """Hashea la contraseña usando Bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT con la información proporcionada y un tiempo de expiración."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Obtiene el usuario actual a partir del token JWT proporcionado."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.isdecimal():
            raise credentials_exception
        user_id = int(subject)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cuenta de usuario inactiva"
        )

    return user


def get_current_superadmin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Solo usuarios marcados como SuperAdmin pueden acceder."""
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de SuperAdmin.",
        )
    return current_user


def get_current_tenant_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Solo los administradores de la organización pueden gestionarla."""
    if not current_user.is_tenant_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador de la organización.",
        )
    return current_user