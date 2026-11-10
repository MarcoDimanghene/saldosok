"""Add province to companies and allow supplier records without CUIT/CUIL.

Run with: python -m database.migrate_supplier_location_and_optional_tax_id
"""

from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

with engine.begin() as connection:
    connection.execute(text(
        "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS provincia VARCHAR"
    ))
    connection.execute(text(
        "ALTER TABLE clientes ALTER COLUMN cuit DROP NOT NULL"
    ))

print("Provincia agregada y CUIT/CUIL opcional habilitado.")
