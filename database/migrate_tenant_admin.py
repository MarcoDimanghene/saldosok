# ==================================================
# MIGRACIÓN: rol de administrador de organización
# ==================================================
# Uso: python -m database.migrate_tenant_admin
# Las cuentas existentes quedan sin privilegios administrativos.
# Un operador debe promover manualmente una cuenta verificada por organización.
# Ejemplo de promoción, verificando el CUIT de la organización:
# UPDATE usuarios SET is_tenant_admin = TRUE
# WHERE email = '<email-verificado>'
#   AND tenant_id = (SELECT id FROM organizaciones WHERE cuit = '<cuit-organizacion>');

from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    conn.execute(
        text(
            "ALTER TABLE usuarios "
            "ADD COLUMN IF NOT EXISTS is_tenant_admin BOOLEAN NOT NULL DEFAULT FALSE"
        )
    )
    conn.commit()
    row = conn.execute(
        text(
            "SELECT column_name, data_type, column_default "
            "FROM information_schema.columns "
            "WHERE table_name = 'usuarios' AND column_name = 'is_tenant_admin'"
        )
    ).fetchone()
    print(f"Columna 'is_tenant_admin' lista: {row}")
