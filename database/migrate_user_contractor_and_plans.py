"""Move service ownership to users and update tenant plan limits.

Run with: python -m database.migrate_user_contractor_and_plans
"""

from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

with engine.begin() as connection:
    connection.execute(text(
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS dni VARCHAR(8)"
    ))
    connection.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'uq_usuarios_dni'
                  AND conrelid = 'usuarios'::regclass
            ) THEN
                ALTER TABLE usuarios
                ADD CONSTRAINT uq_usuarios_dni UNIQUE (dni);
            END IF;
        END
        $$;
    """))
    connection.execute(text(
        "ALTER TABLE organizaciones ALTER COLUMN cuit DROP NOT NULL"
    ))
    connection.execute(text(
        "ALTER TABLE organizaciones ALTER COLUMN razon_social DROP NOT NULL"
    ))
    connection.execute(text(
        "UPDATE organizaciones SET plan = 'moderado' WHERE plan = 'avanzado'"
    ))

print("Titulares de usuario, perfil de empresa opcional y planes actualizados.")
