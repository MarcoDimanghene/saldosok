"""Add issuer, customer, and supplier contact data to tenant companies.

Run with: python -m database.migrate_company_contact_data
"""

from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

COMPANY_COLUMNS = {
    "banco_principal": "VARCHAR",
    "cbu_propio": "VARCHAR",
    "alias_propio": "VARCHAR",
    "localidad": "VARCHAR",
    "banco": "VARCHAR",
    "cbu_cvu": "VARCHAR",
    "alias_cbu": "VARCHAR",
    "titular_cuenta": "VARCHAR",
    "categoria_servicio": "VARCHAR",
    "dias_credito": "INTEGER NOT NULL DEFAULT 0",
    "contacto_nombre": "VARCHAR",
    "email_1": "VARCHAR",
    "email_2": "VARCHAR",
    "telefono_1": "VARCHAR",
    "telefono_2": "VARCHAR",
    "observaciones": "TEXT",
}


with engine.begin() as connection:
    for column, definition in COMPANY_COLUMNS.items():
        connection.execute(text(
            f"ALTER TABLE clientes ADD COLUMN IF NOT EXISTS {column} {definition}"
        ))

print("Datos fiscales, bancarios y de contacto agregados a clientes.")
