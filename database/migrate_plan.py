# ==================================================
# MIGRACIÓN: columna "plan" en tabla organizaciones
# ==================================================
# Uso:  python database/migrate_plan.py
# Requiere la base de datos levantada (docker compose up -d)
# Ejecuta ALTER TABLE solo si la columna no existe (idempotente).

from sqlalchemy import create_engine, text
from database.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE organizaciones "
        "ADD COLUMN IF NOT EXISTS plan VARCHAR(20) NOT NULL DEFAULT 'basico'"
    ))
    conn.commit()
    row = conn.execute(text(
        "SELECT column_name, data_type, column_default "
        "FROM information_schema.columns "
        "WHERE table_name = 'organizaciones' AND column_name = 'plan'"
    )).fetchone()
    print(f"Columna 'plan' lista: {row}")