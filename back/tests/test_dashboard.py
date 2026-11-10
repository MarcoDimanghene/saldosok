import unittest
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models
from back.crud.dashboard import get_dashboard_summary
from database.database import Base


class DashboardCollectionForecastTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.tenant = models.Tenant(
            cuit="30111111111",
            razon_social="Tenant dashboard",
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

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_collection_forecast_uses_period_dates_and_outstanding_balances(self):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        first_of_month = today.replace(day=1)
        first_of_next_month = (first_of_month + timedelta(days=32)).replace(day=1)

        invoices = [
            (start_of_week, Decimal("100.00"), Decimal("25.00")),
            (start_of_week + timedelta(days=7), Decimal("200.00"), Decimal("0.00")),
            (first_of_month, Decimal("300.00"), Decimal("0.00")),
            (first_of_next_month, Decimal("400.00"), Decimal("0.00")),
            (first_of_month, Decimal("500.00"), Decimal("500.00")),
        ]
        for due_date, amount, collected in invoices:
            invoice = models.SalesInvoice(
                tenant_id=self.tenant.id,
                cliente_id=self.company.id,
                fecha_pago_approx=due_date,
                monto_total=amount,
                estado="pagado" if collected == amount else (
                    "parcial" if collected else "pendiente"
                ),
            )
            self.session.add(invoice)
            self.session.flush()
            if collected:
                self.session.add(
                    models.SalesCollection(
                        tenant_id=self.tenant.id,
                        factura_venta_id=invoice.id,
                        monto=collected,
                    )
                )
        self.session.commit()

        summary = get_dashboard_summary(self.session, self.tenant.id)

        start_of_next_week = start_of_week + timedelta(days=7)
        end_of_week = start_of_week + timedelta(days=6)
        end_of_next_week = start_of_next_week + timedelta(days=6)
        end_of_month = first_of_next_month - timedelta(days=1)
        first_of_month_after_next = (
            first_of_next_month + timedelta(days=32)
        ).replace(day=1)
        end_of_next_month = first_of_month_after_next - timedelta(days=1)

        def expected_amount(start, end):
            return sum(
                (
                    amount - collected
                    for due_date, amount, collected in invoices
                    if start <= due_date <= end
                ),
                Decimal("0.00"),
            )

        self.assertEqual(
            Decimal(summary["collections_this_week"]),
            expected_amount(start_of_week, end_of_week),
        )
        self.assertEqual(
            Decimal(summary["collections_next_week"]),
            expected_amount(start_of_next_week, end_of_next_week),
        )
        self.assertEqual(
            Decimal(summary["collections_this_month"]),
            expected_amount(first_of_month, end_of_month),
        )
        self.assertEqual(
            Decimal(summary["collections_next_month"]),
            expected_amount(first_of_next_month, end_of_next_month),
        )


if __name__ == "__main__":
    unittest.main()
