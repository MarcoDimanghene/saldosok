# ==================================================
# MIGRACIÓN: rol explícito de SuperAdmin en usuarios
# ==================================================
# Uso: python -m database.migrate_superadmin
# Ejecutar una vez antes de desplegar la versión que comprueba el nuevo campo.
# Las cuentas existentes quedan como usuarios normales.
# Para otorgar el rol, un operador debe seleccionar y verificar primero una cuenta
# de confianza y actualizarla directamente en la base de datos.

from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    conn.execute(
        text(
            "ALTER TABLE usuarios "
            "ADD COLUMN IF NOT EXISTS is_superadmin BOOLEAN NOT NULL DEFAULT FALSE"
        )
    )
    conn.commit()
    row = conn.execute(
        text(
            "SELECT column_name, data_type, column_default "
            "FROM information_schema.columns "
            "WHERE table_name = 'usuarios' AND column_name = 'is_superadmin'"
        )
    ).fetchone()
    print(f"Columna 'is_superadmin' lista: {row}")
