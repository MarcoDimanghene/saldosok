"""Add an optional recipient company to purchase invoices.

Run with: python -m database.migrate_purchase_invoice_recipient
"""

from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

with engine.begin() as connection:
    connection.execute(text(
        "ALTER TABLE facturas_compra "
        "ADD COLUMN IF NOT EXISTS receptor_id INTEGER REFERENCES clientes(id)"
    ))
    connection.execute(text(
        """
        UPDATE facturas_compra AS purchase
        SET receptor_id = company.id
        FROM organizaciones tenant
        JOIN clientes company
          ON company.tenant_id = tenant.id
         AND regexp_replace(company.cuit, '[^0-9]', '', 'g')
             = regexp_replace(tenant.cuit, '[^0-9]', '', 'g')
        WHERE purchase.tenant_id = tenant.id
          AND purchase.receptor_id IS NULL
        """
    ))

print("Migración de destinatarios de facturas de compra finalizada.")
