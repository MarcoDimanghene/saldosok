"""Migrate issuer companies and internally numbered pending purchases.

Run with: python -m database.migrate_invoice_entities
"""

from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

with engine.begin() as conn:
    conn.execute(text(
        "ALTER TABLE clientes DROP CONSTRAINT IF EXISTS clientes_cuit_key"
    ))
    conn.execute(text(
        "DROP INDEX IF EXISTS clientes_cuit_key"
    ))
    conn.execute(text(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_clientes_tenant_cuit
        ON clientes (tenant_id, cuit)
        """
    ))
    conn.execute(text(
        "ALTER TABLE clientes "
        "ADD COLUMN IF NOT EXISTS es_emisor BOOLEAN NOT NULL DEFAULT FALSE"
    ))
    conn.execute(text(
        """
        INSERT INTO clientes (
            cuit, razon_social, condicion_iva, domicilio,
            es_cliente, es_proveedor, es_emisor, tenant_id
        )
        SELECT o.cuit, o.razon_social, o.condicion_iva, o.domicilio,
               FALSE, FALSE, TRUE, o.id
        FROM organizaciones o
        WHERE NOT EXISTS (
            SELECT 1 FROM clientes c
            WHERE c.tenant_id = o.id AND c.cuit = o.cuit
        )
        """
    ))
    conn.execute(text(
        """
        UPDATE clientes c
        SET es_emisor = TRUE
        FROM organizaciones o
        WHERE c.tenant_id = o.id AND c.cuit = o.cuit
        """
    ))
    conn.execute(text(
        """
        UPDATE clientes c SET es_cliente = TRUE
        WHERE EXISTS (
            SELECT 1 FROM facturas_venta f
            WHERE f.cliente_id = c.id AND f.tenant_id = c.tenant_id
        )
        """
    ))
    conn.execute(text(
        """
        UPDATE clientes c SET es_proveedor = TRUE
        WHERE EXISTS (
            SELECT 1 FROM facturas_compra f
            WHERE f.proveedor_id = c.id AND f.tenant_id = c.tenant_id
        )
        """
    ))
    conn.execute(text(
        "ALTER TABLE facturas_venta "
        "ADD COLUMN IF NOT EXISTS emisor_id INTEGER REFERENCES clientes(id)"
    ))
    conn.execute(text(
        """
        UPDATE facturas_venta f
        SET emisor_id = c.id
        FROM organizaciones o
        JOIN clientes c ON c.tenant_id = o.id AND c.cuit = o.cuit
        WHERE f.tenant_id = o.id AND f.emisor_id IS NULL
        """
    ))
    conn.execute(text(
        "ALTER TABLE facturas_compra "
        "ADD COLUMN IF NOT EXISTS numero_interno VARCHAR"
    ))
    conn.execute(text(
        "ALTER TABLE facturas_compra "
        "ADD COLUMN IF NOT EXISTS factura_recibida BOOLEAN NOT NULL DEFAULT TRUE"
    ))
    conn.execute(text(
        "ALTER TABLE facturas_compra ADD COLUMN IF NOT EXISTS concepto TEXT"
    ))
    conn.execute(text(
        """
        UPDATE facturas_compra
        SET numero_interno = 'COMP-' || tenant_id::text || '-'
            || lpad(id::text, 6, '0')
        WHERE numero_interno IS NULL
        """
    ))
    conn.execute(text(
        "ALTER TABLE facturas_compra ALTER COLUMN numero_interno SET NOT NULL"
    ))
    conn.execute(text(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS
        uq_facturas_compra_numero_interno
        ON facturas_compra (numero_interno)
        """
    ))

print("Migración de emisores y compras pendientes finalizada.")
