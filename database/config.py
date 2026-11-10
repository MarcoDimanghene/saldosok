from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Variables de Base de Datos
    DATABASE_URL: str
    
    # Variables de Seguridad / JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SMTP_USE_TLS: bool = True
    FRONTEND_URL: str = "http://localhost:5173"

    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=".env",            # Si config.py está en la carpeta raíz. Usa "../.env" si está dentro de /back
        env_file_encoding="utf-8",
        extra="ignore"              # Ignora variables adicionales si no están definidas en esta clase
    )

settings = Settings()