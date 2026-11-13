import unittest
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models
from back.crud.audit import get_audit_logs
from back.crud.invoices import create_purchase_invoice, create_sales_invoice
from back.crud.payments import create_collection, create_payment
from back.schemas.invoices import PurchaseInvoiceCreate, SalesInvoiceCreate
from back.schemas.payments import CollectionCreate, PaymentCreate
from back.services.audit import record_audit_event
from database.database import Base


class AuditLogTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.first_tenant = models.Tenant(razon_social="Organización 1")
        self.second_tenant = models.Tenant(razon_social="Organización 2")
        self.session.add_all([self.first_tenant, self.second_tenant])
        self.session.flush()
        self.actor = models.User(
            username="admin",
            email="admin@example.com",
            hashed_password="must-not-be-audited",
            tenant_id=self.first_tenant.id,
            is_tenant_admin=True,
        )
        self.session.add(self.actor)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_audit_entries_are_tenant_scoped_and_exclude_secrets(self):
        self.session.info["audit_actor_id"] = self.actor.id
        record_audit_event(
            self.session,
            tenant_id=self.first_tenant.id,
            action="updated",
            entity_type="sales_invoice",
            entity_id=42,
            before_data={"amount": "10.00"},
            after_data={
                "amount": "20.00",
                "password": "do-not-store",
                "metadata": {"token_hash": "do-not-store"},
            },
        )
        record_audit_event(
            self.session,
            tenant_id=self.second_tenant.id,
            action="deleted",
            entity_type="purchase_payment",
            entity_id=17,
        )
        self.session.commit()

        entries = get_audit_logs(self.session, self.first_tenant.id)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].actor_user_id, self.actor.id)
        self.assertEqual(entries[0].after_data["amount"], "20.00")
        self.assertNotIn("password", entries[0].after_data)
        self.assertNotIn("token_hash", entries[0].after_data["metadata"])

    def test_invoice_and_payment_changes_are_audited_in_their_transaction(self):
        issuer = models.Company(
            razon_social="Emisora",
            es_emisor=True,
            tenant_id=self.first_tenant.id,
        )
        client = models.Company(
            razon_social="Cliente",
            es_cliente=True,
            tenant_id=self.first_tenant.id,
        )
        supplier = models.Company(
            razon_social="Proveedor",
            es_proveedor=True,
            tenant_id=self.first_tenant.id,
        )
        self.session.add_all([issuer, client, supplier])
        self.session.commit()
        self.session.info["audit_actor_id"] = self.actor.id

        sale = create_sales_invoice(
            self.session,
            self.first_tenant.id,
            SalesInvoiceCreate(
                issuer_id=issuer.id,
                receiver_id=client.id,
                letter="A",
                point_of_sale=1,
                invoice_number=10,
                issue_date=date(2026, 1, 1),
                estimated_payment_date=date(2026, 1, 31),
                total_amount=Decimal("100.00"),
            ),
        )
        purchase = create_purchase_invoice(
            self.session,
            self.first_tenant.id,
            PurchaseInvoiceCreate(
                issuer_id=supplier.id,
                letter="A",
                point_of_sale=2,
                invoice_number=20,
                issue_date=date(2026, 1, 2),
                due_date=date(2026, 2, 1),
                total_amount=Decimal("80.00"),
            ),
        )
        create_collection(
            self.session,
            self.first_tenant.id,
            CollectionCreate(
                invoice_id=sale.id,
                amount=Decimal("25.00"),
                collection_date=date(2026, 1, 10),
            ),
        )
        create_payment(
            self.session,
            self.first_tenant.id,
            PaymentCreate(
                invoice_id=purchase.id,
                amount=Decimal("30.00"),
                payment_date=date(2026, 1, 11),
            ),
        )

        entries = get_audit_logs(self.session, self.first_tenant.id, limit=10)

        self.assertEqual(
            {entry.entity_type for entry in entries},
            {"sales_invoice", "purchase_invoice", "sales_collection", "purchase_payment"},
        )
        self.assertTrue(all(entry.actor_user_id == self.actor.id for entry in entries))


if __name__ == "__main__":
    unittest.main()
