import unittest
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models, schemas
from back.crud.invoices import create_pending_purchase, create_purchase_invoice
from back.crud.operating_results import (
    create_operating_result,
    list_operating_results,
    update_operating_result,
)
from database.database import Base


class OperatingResultTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.tenant = models.Tenant(
            cuit="30111111111",
            razon_social="Organización local",
            condicion_iva="Responsable Inscripto",
        )
        self.other_tenant = models.Tenant(
            cuit="30222222222",
            razon_social="Organización externa",
            condicion_iva="Responsable Inscripto",
        )
        self.session.add_all([self.tenant, self.other_tenant])
        self.session.flush()
        self.supplier = models.Company(
            cuit="20111111111",
            razon_social="Proveedor local",
            tenant_id=self.tenant.id,
            es_proveedor=True,
        )
        self.other_supplier = models.Company(
            cuit="20222222222",
            razon_social="Proveedor externo",
            tenant_id=self.other_tenant.id,
            es_proveedor=True,
        )
        self.session.add_all([self.supplier, self.other_supplier])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def create_invoice(self, supplier, amount=Decimal("100.00")):
        return create_purchase_invoice(
            self.session,
            supplier.tenant_id,
            schemas.PurchaseInvoiceCreate(
                issuer_id=supplier.id,
                letter="A",
                point_of_sale=1,
                invoice_number=1,
                issue_date=date(2026, 1, 1),
                total_amount=amount,
            ),
        )

    def test_profit_and_percentage_use_sale_amount_and_adjusted_cost(self):
        invoice = self.create_invoice(self.supplier)
        create_purchase_invoice(
            self.session,
            self.tenant.id,
            schemas.PurchaseInvoiceCreate(
                issuer_id=self.supplier.id,
                letter="A",
                point_of_sale=1,
                invoice_number=2,
                issue_date=date(2026, 1, 2),
                total_amount=Decimal("20.00"),
                tipo_comprobante="nota_credito",
                factura_origen_id=invoice.id,
            ),
        )

        result = create_operating_result(
            self.session,
            self.tenant.id,
            schemas.OperatingResultCreate(
                factura_compra_id=invoice.id,
                monto_venta=Decimal("150.00"),
            ),
        )

        self.assertEqual(result.monto_compra, Decimal("80.00"))
        self.assertEqual(result.ganancia, Decimal("70.00"))
        self.assertEqual(result.porcentaje_venta, Decimal("46.67"))
        self.assertEqual(len(list_operating_results(self.session, self.tenant.id)), 1)

        updated = update_operating_result(
            self.session,
            self.tenant.id,
            result.id,
            schemas.OperatingResultUpdate(monto_venta=Decimal("140.00")),
        )
        self.assertEqual(updated.ganancia, Decimal("60.00"))
        self.assertEqual(updated.porcentaje_venta, Decimal("42.86"))

    def test_result_rejects_foreign_or_non_formal_purchase_invoices(self):
        foreign_invoice = self.create_invoice(self.other_supplier)
        pending_purchase = create_pending_purchase(
            self.session,
            self.tenant.id,
            schemas.PurchasePendingCreate(
                supplier_id=self.supplier.id,
                concept="Compra pendiente",
                total_amount=Decimal("50.00"),
            ),
        )
        data = lambda invoice_id: schemas.OperatingResultCreate(
            factura_compra_id=invoice_id,
            monto_venta=Decimal("60.00"),
        )

        for invoice_id in (foreign_invoice.id, pending_purchase.id):
            with self.subTest(invoice_id=invoice_id):
                with self.assertRaises(HTTPException) as error:
                    create_operating_result(self.session, self.tenant.id, data(invoice_id))
                self.assertEqual(error.exception.status_code, 404)

    def test_invoice_can_have_only_one_operating_result(self):
        invoice = self.create_invoice(self.supplier)
        data = schemas.OperatingResultCreate(
            factura_compra_id=invoice.id,
            monto_venta=Decimal("125.00"),
        )
        create_operating_result(self.session, self.tenant.id, data)

        with self.assertRaises(HTTPException) as error:
            create_operating_result(self.session, self.tenant.id, data)

        self.assertEqual(error.exception.status_code, 409)
