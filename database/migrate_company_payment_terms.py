"""Split company credit days into collection and payment terms.

Run with: python -m database.migrate_company_payment_terms
"""

from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

with engine.begin() as connection:
    connection.execute(text(
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS dias_cobro INTEGER"
    ))
    connection.execute(text(
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS dias_pago INTEGER"
    ))
    connection.execute(text(
        """
        UPDATE clientes
        SET dias_cobro = COALESCE(dias_cobro, dias_credito, 0),
            dias_pago = COALESCE(dias_pago, dias_credito, 0)
        """
    ))
    connection.execute(text(
        "ALTER TABLE clientes ALTER COLUMN dias_cobro SET DEFAULT 0"
    ))
    connection.execute(text(
        "ALTER TABLE clientes ALTER COLUMN dias_cobro SET NOT NULL"
    ))
    connection.execute(text(
        "ALTER TABLE clientes ALTER COLUMN dias_pago SET DEFAULT 0"
    ))
    connection.execute(text(
        "ALTER TABLE clientes ALTER COLUMN dias_pago SET NOT NULL"
    ))

print("Plazos de cobro y pago agregados a empresas.")
