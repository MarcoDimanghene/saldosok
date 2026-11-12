import unittest
from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models
from back.crud.dashboard import get_dashboard_summary
from back.crud.invoices import (
    complete_pending_purchase,
    create_purchase_invoice,
    create_pending_purchase,
    create_sales_invoice,
    update_purchase_invoice,
    update_sales_invoice,
)
from back.models import PurchasePayment, SalesCollection
from back.schemas.invoices import (
    PurchaseInvoiceComplete,
    PurchaseInvoiceCreate,
    PurchasePendingCreate,
    PurchaseInvoiceUpdate,
    SalesInvoiceCreate,
    SalesInvoiceUpdate,
)
from back.crud.payments import create_payment
from back.schemas.payments import PaymentCreate
from database.database import Base


class InvoiceTenantIsolationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.tenant = models.Tenant(
            cuit="30111111111",
            razon_social="Tenant local",
            condicion_iva="Responsable Inscripto",
        )
        self.other_tenant = models.Tenant(
            cuit="30222222222",
            razon_social="Tenant externo",
            condicion_iva="Responsable Inscripto",
        )
        self.session.add_all([self.tenant, self.other_tenant])
        self.session.flush()

        self.local_company = models.Company(
            cuit="20111111111",
            razon_social="Empresa local",
            tenant_id=self.tenant.id,
            es_cliente=True,
            es_proveedor=True,
            es_emisor=True,
        )
        self.foreign_company = models.Company(
            cuit="20222222222",
            razon_social="Empresa externa",
            tenant_id=self.other_tenant.id,
        )
        self.session.add_all([self.local_company, self.foreign_company])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def sales_invoice_data(self, receiver_id):
        return SalesInvoiceCreate(
            issuer_id=self.local_company.id,
            receiver_id=receiver_id,
            letter="A",
            point_of_sale=1,
            invoice_number=1,
            issue_date=date.today(),
            estimated_payment_date=date.today(),
            total_amount=Decimal("100.00"),
        )

    def purchase_invoice_data(self, issuer_id):
        return PurchaseInvoiceCreate(
            issuer_id=issuer_id,
            letter="A",
            point_of_sale=1,
            invoice_number=1,
            issue_date=date.today(),
            total_amount=Decimal("100.00"),
        )

    def test_sales_debit_note_can_be_created_and_linked_to_its_invoice(self):
        origin = create_sales_invoice(
            self.session,
            self.tenant.id,
            self.sales_invoice_data(self.local_company.id),
        )
        note_data = self.sales_invoice_data(self.local_company.id).model_copy(
            update={
                "invoice_number": 2,
                "tipo_comprobante": "nota_debito",
                "factura_origen_id": origin.id,
            }
        )

        note = create_sales_invoice(self.session, self.tenant.id, note_data)

        self.assertEqual(note.tipo_comprobante, "nota_debito")
        self.assertEqual(note.factura_origen_id, origin.id)

    def test_purchase_credit_note_can_be_created_without_receiver_id(self):
        origin = create_purchase_invoice(
            self.session,
            self.tenant.id,
            self.purchase_invoice_data(self.local_company.id),
        )
        note_data = self.purchase_invoice_data(self.local_company.id).model_copy(
            update={
                "invoice_number": 2,
                "tipo_comprobante": "nota_credito",
                "factura_origen_id": origin.id,
            }
        )

        note = create_purchase_invoice(self.session, self.tenant.id, note_data)

        self.assertEqual(note.tipo_comprobante, "nota_credito")
        self.assertEqual(note.factura_origen_id, origin.id)

    def test_pending_purchase_gets_system_number_and_can_be_completed_after_payment(self):
        purchase = create_pending_purchase(
            self.session,
            self.tenant.id,
            PurchasePendingCreate(
                supplier_id=self.local_company.id,
                concept="Servicio de mantenimiento",
                total_amount=Decimal("100.00"),
                due_date=date.today(),
            ),
        )
        self.assertFalse(purchase.factura_recibida)
        self.assertTrue(purchase.numero_interno.startswith(f"COMP-{self.tenant.id}-"))
        internal_number = purchase.numero_interno

        create_payment(
            self.session,
            self.tenant.id,
            PaymentCreate(
                invoice_id=purchase.id,
                amount=Decimal("40.00"),
                payment_date=date.today(),
            ),
        )
        completed = complete_pending_purchase(
            self.session,
            self.tenant.id,
            purchase.id,
            PurchaseInvoiceComplete(
                letter="A",
                point_of_sale=1,
                invoice_number=258,
                issue_date=date.today(),
                total_amount=Decimal("100.00"),
            ),
        )

        self.assertTrue(completed.factura_recibida)
        self.assertEqual(completed.numero_interno, internal_number)
        self.assertEqual(completed.estado, "parcial")
        self.assertEqual(get_dashboard_summary(self.session, self.tenant.id)["accounts_payable"], Decimal("60.00"))

    def test_pending_purchase_rejects_supplier_from_another_tenant(self):
        with self.assertRaises(HTTPException) as error:
            create_pending_purchase(
                self.session,
                self.tenant.id,
                PurchasePendingCreate(
                    supplier_id=self.foreign_company.id,
                    concept="Compra no autorizada",
                    total_amount=Decimal("50.00"),
                ),
            )

        self.assertEqual(error.exception.status_code, 404)

    def test_formal_invoice_cannot_be_lower_than_already_paid_amount(self):
        purchase = create_pending_purchase(
            self.session,
            self.tenant.id,
            PurchasePendingCreate(
                supplier_id=self.local_company.id,
                concept="Compra con anticipo",
                total_amount=Decimal("100.00"),
            ),
        )
        create_payment(
            self.session,
            self.tenant.id,
            PaymentCreate(
                invoice_id=purchase.id,
                amount=Decimal("40.00"),
                payment_date=date.today(),
            ),
        )

        with self.assertRaises(HTTPException) as error:
            complete_pending_purchase(
                self.session,
                self.tenant.id,
                purchase.id,
                PurchaseInvoiceComplete(
                    letter="A",
                    point_of_sale=1,
                    invoice_number=259,
                    issue_date=date.today(),
                    total_amount=Decimal("30.00"),
                ),
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertFalse(purchase.factura_recibida)
        self.assertEqual(purchase.monto_total, Decimal("100.00"))

    def test_sales_invoice_rejects_company_from_another_tenant(self):
        with self.assertRaises(HTTPException) as error:
            create_sales_invoice(
                self.session,
                self.tenant.id,
                self.sales_invoice_data(self.foreign_company.id),
            )

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)

    def test_sales_invoice_requires_a_tenant_owned_issuer(self):
        data = self.sales_invoice_data(self.local_company.id).model_copy(
            update={"issuer_id": self.foreign_company.id}
        )

        with self.assertRaises(HTTPException) as error:
            create_sales_invoice(self.session, self.tenant.id, data)

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)

    def test_sales_invoice_rejects_company_not_marked_as_issuer(self):
        self.local_company.es_emisor = False
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            create_sales_invoice(
                self.session,
                self.tenant.id,
                self.sales_invoice_data(self.local_company.id),
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)

    def test_sales_invoice_status_starts_pending_until_a_collection_is_applied(self):
        data = self.sales_invoice_data(self.local_company.id).model_copy(
            update={"status": "pagado"}
        )

        invoice = create_sales_invoice(self.session, self.tenant.id, data)

        self.assertEqual(invoice.estado, "pendiente")

    def test_sales_invoice_tracks_multiple_issuers_under_one_tenant(self):
        second_issuer = models.Company(
            cuit="20333333333",
            razon_social="Segunda empresa emisora",
            tenant_id=self.tenant.id,
            es_emisor=True,
        )
        self.session.add(second_issuer)
        self.session.commit()

        first_invoice = create_sales_invoice(
            self.session,
            self.tenant.id,
            self.sales_invoice_data(self.local_company.id),
        )
        second_data = self.sales_invoice_data(self.local_company.id).model_copy(
            update={"issuer_id": second_issuer.id, "invoice_number": 2}
        )
        second_invoice = create_sales_invoice(self.session, self.tenant.id, second_data)

        self.assertEqual(first_invoice.emisor_id, self.local_company.id)
        self.assertEqual(second_invoice.emisor_id, second_issuer.id)

    def test_same_external_company_can_be_registered_for_different_tenants(self):
        company_copy = models.Company(
            cuit=self.local_company.cuit,
            razon_social=self.local_company.razon_social,
            tenant_id=self.other_tenant.id,
        )
        self.session.add(company_copy)
        self.session.commit()

        self.assertNotEqual(company_copy.id, self.local_company.id)
        self.assertEqual(company_copy.cuit, self.local_company.cuit)

    def test_purchase_invoice_rejects_company_from_another_tenant(self):
        with self.assertRaises(HTTPException) as error:
            create_purchase_invoice(
                self.session,
                self.tenant.id,
                self.purchase_invoice_data(self.foreign_company.id),
            )

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(self.session.query(models.PurchaseInvoice).count(), 0)

    def test_sales_invoice_update_rejects_company_from_another_tenant(self):
        invoice = create_sales_invoice(
            self.session,
            self.tenant.id,
            self.sales_invoice_data(self.local_company.id),
        )

        with self.assertRaises(HTTPException) as error:
            update_sales_invoice(
                self.session,
                self.tenant.id,
                invoice.id,
                SalesInvoiceUpdate(receiver_id=self.foreign_company.id),
            )

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(invoice.cliente_id, self.local_company.id)

    def test_purchase_invoice_update_rejects_company_from_another_tenant(self):
        invoice = create_purchase_invoice(
            self.session,
            self.tenant.id,
            self.purchase_invoice_data(self.local_company.id),
        )

        with self.assertRaises(HTTPException) as error:
            update_purchase_invoice(
                self.session,
                self.tenant.id,
                invoice.id,
                PurchaseInvoiceUpdate(issuer_id=self.foreign_company.id),
            )

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(invoice.proveedor_id, self.local_company.id)

    def test_dashboard_hides_foreign_company_linked_to_legacy_invoice(self):
        self.session.add(
            models.SalesInvoice(
                tenant_id=self.tenant.id,
                cliente_id=self.foreign_company.id,
                letra="A",
                punto_venta=1,
                nro_factura=1,
                fecha_emision=date.today(),
                fecha_pago_approx=date.today(),
                monto_total=Decimal("100.00"),
            )
        )
        self.session.commit()

        summary = get_dashboard_summary(self.session, self.tenant.id)

        self.assertEqual(summary["top_clients"], [])

    def test_dashboard_due_amounts_use_outstanding_balance_for_partial_invoices(self):
        today = date.today()
        overdue_sales = models.SalesInvoice(
            tenant_id=self.tenant.id,
            cliente_id=self.local_company.id,
            monto_total=Decimal("100.00"),
            fecha_pago_approx=today - timedelta(days=1),
            estado="parcial",
        )
        upcoming_sales = models.SalesInvoice(
            tenant_id=self.tenant.id,
            cliente_id=self.local_company.id,
            monto_total=Decimal("100.00"),
            fecha_pago_approx=today + timedelta(days=2),
            estado="parcial",
        )
        overdue_purchase = models.PurchaseInvoice(
            tenant_id=self.tenant.id,
            proveedor_id=self.local_company.id,
            monto_total=Decimal("100.00"),
            fecha_vencimiento=today - timedelta(days=1),
            estado="parcial",
        )
        upcoming_purchase = models.PurchaseInvoice(
            tenant_id=self.tenant.id,
            proveedor_id=self.local_company.id,
            monto_total=Decimal("100.00"),
            fecha_vencimiento=today + timedelta(days=2),
            estado="parcial",
        )
        self.session.add_all(
            [overdue_sales, upcoming_sales, overdue_purchase, upcoming_purchase]
        )
        self.session.flush()
        self.session.add_all([
            SalesCollection(
                tenant_id=self.tenant.id,
                factura_venta_id=overdue_sales.id,
                monto=Decimal("60.00"),
            ),
            SalesCollection(
                tenant_id=self.tenant.id,
                factura_venta_id=upcoming_sales.id,
                monto=Decimal("25.00"),
            ),
            PurchasePayment(
                tenant_id=self.tenant.id,
                factura_compra_id=overdue_purchase.id,
                monto=Decimal("70.00"),
            ),
            PurchasePayment(
                tenant_id=self.tenant.id,
                factura_compra_id=upcoming_purchase.id,
                monto=Decimal("10.00"),
            ),
        ])
        self.session.commit()

        summary = get_dashboard_summary(self.session, self.tenant.id)

        self.assertEqual(summary["overdue_sales_count"], 1)
        self.assertEqual(summary["overdue_sales_amount"], Decimal("40.00"))
        self.assertEqual(summary["overdue_purchases_count"], 1)
        self.assertEqual(summary["overdue_purchases_amount"], Decimal("30.00"))
        self.assertEqual(summary["upcoming_collections"][0]["monto"], Decimal("75.00"))
        self.assertEqual(summary["upcoming_payments"][0]["monto"], Decimal("90.00"))


if __name__ == "__main__":
    unittest.main()
