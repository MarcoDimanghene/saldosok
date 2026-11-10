import unittest
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models
from back.crud.payments import (
    create_collection,
    create_payment,
    delete_collection,
    update_collection,
    update_payment,
)
from back.schemas.payments import CollectionCreate, PaymentCreate
from database.database import Base


class PaymentValidationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.tenant = models.Tenant(
            cuit="30111111111",
            razon_social="Tenant pagos",
            condicion_iva="Responsable Inscripto",
        )
        self.session.add(self.tenant)
        self.session.flush()
        self.company = models.Company(
            cuit="20111111111",
            razon_social="Empresa de prueba",
            tenant_id=self.tenant.id,
        )
        self.session.add(self.company)
        self.session.flush()
        self.sales_invoice = models.SalesInvoice(
            tenant_id=self.tenant.id,
            cliente_id=self.company.id,
            monto_total=Decimal("100.00"),
            estado="pendiente",
        )
        self.purchase_invoice = models.PurchaseInvoice(
            tenant_id=self.tenant.id,
            proveedor_id=self.company.id,
            monto_total=Decimal("100.00"),
            estado="pendiente",
        )
        self.session.add_all([self.sales_invoice, self.purchase_invoice])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def collection_data(self, amount):
        return CollectionCreate(
            invoice_id=self.sales_invoice.id,
            amount=amount,
            collection_date=date.today(),
        )

    def payment_data(self, amount):
        return PaymentCreate(
            invoice_id=self.purchase_invoice.id,
            amount=amount,
            payment_date=date.today(),
        )

    def test_schemas_reject_zero_and_negative_amounts(self):
        for amount in (Decimal("0"), Decimal("-1")):
            with self.subTest(amount=amount):
                with self.assertRaises(ValidationError):
                    self.collection_data(amount)
                with self.assertRaises(ValidationError):
                    self.payment_data(amount)

    def test_collection_cannot_exceed_invoice_balance(self):
        with self.assertRaises(HTTPException) as error:
            create_collection(self.session, self.tenant.id, self.collection_data("100.01"))

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(self.sales_invoice.estado, "pendiente")

    def test_payment_cannot_exceed_invoice_balance(self):
        with self.assertRaises(HTTPException) as error:
            create_payment(self.session, self.tenant.id, self.payment_data("100.01"))

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(self.purchase_invoice.estado, "pendiente")

    def test_updating_collection_rejects_amount_over_remaining_balance(self):
        first = create_collection(
            self.session, self.tenant.id, self.collection_data("60.00")
        )
        second = create_collection(
            self.session, self.tenant.id, self.collection_data("30.00")
        )

        with self.assertRaises(HTTPException) as error:
            update_collection(
                self.session,
                self.tenant.id,
                second.id,
                self.collection_data("50.00"),
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(second.monto, Decimal("30.00"))
        self.assertEqual(self.sales_invoice.estado, "parcial")
        self.assertEqual(first.monto + second.monto, Decimal("90.00"))

    def test_updating_payment_rejects_amount_over_remaining_balance(self):
        first = create_payment(self.session, self.tenant.id, self.payment_data("60.00"))
        second = create_payment(self.session, self.tenant.id, self.payment_data("30.00"))

        with self.assertRaises(HTTPException) as error:
            update_payment(
                self.session,
                self.tenant.id,
                second.id,
                self.payment_data("50.00"),
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(second.monto, Decimal("30.00"))
        self.assertEqual(self.purchase_invoice.estado, "parcial")
        self.assertEqual(first.monto + second.monto, Decimal("90.00"))

    def test_deleting_collection_recalculates_invoice_status(self):
        collection = create_collection(
            self.session, self.tenant.id, self.collection_data("100.00")
        )
        self.assertEqual(self.sales_invoice.estado, "pagado")

        delete_collection(self.session, self.tenant.id, collection.id)

        self.assertEqual(self.sales_invoice.estado, "pendiente")


if __name__ == "__main__":
    unittest.main()
