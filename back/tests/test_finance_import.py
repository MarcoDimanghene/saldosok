import unittest
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from back import models
from back.schemas.finance_import import FinanceImportRequest
from back.services.finance_import import import_finance_rows
from database.database import Base


class FinanceImportTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.tenant = models.Tenant(
            cuit="30111111111",
            razon_social="Tenant importación",
            condicion_iva="Responsable Inscripto",
        )
        self.session.add(self.tenant)
        self.session.flush()
        self.issuer = self._company("20111111111", "Emisor", issuer=True)
        self.client = self._company("20222222222", "Cliente", client=True)
        self.supplier = self._company("20333333333", "Proveedor", supplier=True)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def _company(self, cuit, name, issuer=False, client=False, supplier=False):
        company = models.Company(
            cuit=cuit,
            razon_social=name,
            tenant_id=self.tenant.id,
            es_emisor=issuer,
            es_cliente=client,
            es_proveedor=supplier,
        )
        self.session.add(company)
        self.session.flush()
        return company

    def _payload(self, **sheets):
        data = {
            "companies": [],
            "sales": [],
            "purchases": [],
            "collections": [],
            "payments": [],
        }
        data.update(sheets)
        return FinanceImportRequest(**data)

    def _sales(self, row_number=2, **overrides):
        row = {
            "rowNumber": row_number,
            "cuit_emisor": self.issuer.cuit,
            "cuit_cliente": self.client.cuit,
            "letra": "A",
            "punto_venta": 1,
            "numero_factura": row_number,
            "fecha_emision": "2026-10-01",
            "fecha_vencimiento": "2026-11-01",
            "importe": "100.00",
        }
        row.update(overrides)
        return row

    def _purchase(self, row_number=2, **overrides):
        row = {
            "rowNumber": row_number,
            "cuit_proveedor": self.supplier.cuit,
            "letra": "A",
            "punto_venta": 1,
            "numero_factura": row_number,
            "fecha_emision": "2026-10-01",
            "fecha_vencimiento": "2026-11-01",
            "importe": "100.00",
            "moneda": "ARS",
        }
        row.update(overrides)
        return row

    def _collection(self, row_number=2, **overrides):
        row = {
            "rowNumber": row_number,
            "cuit_emisor": self.issuer.cuit,
            "cuit_cliente": self.client.cuit,
            "letra": "A",
            "punto_venta": 1,
            "numero_factura": 2,
            "fecha": "2026-10-15",
            "importe": "30.00",
            "medio": "Transferencia",
        }
        row.update(overrides)
        return row

    def _payment(self, row_number=2, **overrides):
        row = {
            "rowNumber": row_number,
            "cuit_proveedor": self.supplier.cuit,
            "letra": "A",
            "punto_venta": 1,
            "numero_factura": 2,
            "fecha": "2026-10-15",
            "importe": "30.00",
            "medio": "Transferencia",
        }
        row.update(overrides)
        return row

    def test_imports_invoices_and_multiple_partial_settlements_atomically(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(
                sales=[self._sales()],
                purchases=[self._purchase()],
                collections=[
                    self._collection(2),
                    self._collection(3, importe="70.00", comprobante="COB-2"),
                ],
                payments=[
                    self._payment(2),
                    self._payment(3, importe="70.00", comprobante="PAG-2"),
                ],
            ),
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["imported"],
            {
                "companies": 0,
                "issuer_updated": False,
                "sales": 1,
                "purchases": 1,
                "collections": 2,
                "payments": 2,
            },
        )
        sales_invoice = self.session.query(models.SalesInvoice).one()
        purchase_invoice = self.session.query(models.PurchaseInvoice).one()
        self.assertEqual(sales_invoice.estado, "pagado")
        self.assertEqual(purchase_invoice.estado, "pagado")
        self.assertEqual(sales_invoice.fecha_pago_approx, date(2026, 11, 1))
        self.assertEqual(
            self.session.query(func.sum(models.SalesCollection.monto)).scalar(),
            Decimal("100.00"),
        )
        self.assertEqual(
            self.session.query(func.sum(models.PurchasePayment.monto)).scalar(),
            Decimal("100.00"),
        )
        self.assertTrue(purchase_invoice.numero_interno.startswith("COMP-"))

    def test_imports_companies_and_uses_them_for_invoices_in_same_workbook(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(
                companies=[
                    {
                        "rowNumber": 2,
                        "cuit": "20444444444",
                        "razon_social": "Nuevo cliente",
                        "es_cliente": "Sí",
                        "es_proveedor": "No",
                        "es_emisor": "No",
                    },
                    {
                        "rowNumber": 3,
                        "cuit": "20555555555",
                        "razon_social": "Nuevo proveedor",
                        "es_cliente": "No",
                        "es_proveedor": "Sí",
                        "es_emisor": "No",
                    },
                ],
                sales=[self._sales(cuit_cliente="20444444444")],
                purchases=[self._purchase(cuit_proveedor="20555555555")],
            ),
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["imported"]["companies"], 2)
        self.assertEqual(result["imported"]["sales"], 1)
        self.assertEqual(result["imported"]["purchases"], 1)
        sales_invoice = self.session.query(models.SalesInvoice).one()
        purchase_invoice = self.session.query(models.PurchaseInvoice).one()
        self.assertEqual(sales_invoice.cliente.razon_social, "Nuevo cliente")
        self.assertEqual(purchase_invoice.proveedor.razon_social, "Nuevo proveedor")

    def test_imported_issuer_updates_organization_profile_and_is_used_by_sales(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(
                companies=[{
                    "rowNumber": 2,
                    "cuit": "20999999999",
                    "razon_social": "Emisor actualizado",
                    "condicion_iva": "Responsable Inscripto",
                    "domicilio": "Calle 123",
                    "es_cliente": "No",
                    "es_proveedor": "No",
                    "es_emisor": "Sí",
                }],
                sales=[self._sales(cuit_emisor="20999999999")],
            ),
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["imported"]["companies"], 0)
        self.assertTrue(result["imported"]["issuer_updated"])
        self.assertEqual(self.tenant.cuit, "20999999999")
        self.assertEqual(self.tenant.razon_social, "Emisor actualizado")
        self.assertEqual(self.issuer.cuit, "20999999999")
        self.assertEqual(self.session.query(models.SalesInvoice).one().emisor, self.issuer)

    def test_imported_issuer_creates_the_organization_profile_when_missing(self):
        tenant = models.Tenant()
        self.session.add(tenant)
        self.session.commit()

        result = import_finance_rows(
            self.session,
            tenant.id,
            self._payload(companies=[{
                "rowNumber": 2,
                "cuit": "20666666666",
                "razon_social": "Nuevo emisor",
                "es_cliente": "No",
                "es_proveedor": "No",
                "es_emisor": "Sí",
            }]),
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["imported"]["companies"], 1)
        self.assertTrue(result["imported"]["issuer_updated"])
        self.assertEqual(tenant.cuit, "20666666666")
        self.assertEqual(
            self.session.query(models.Company).filter_by(
                tenant_id=tenant.id,
                es_emisor=True,
            ).count(),
            1,
        )

    def test_invalid_import_does_not_update_issuer_profile(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(
                companies=[{
                    "rowNumber": 2,
                    "cuit": "20999999999",
                    "razon_social": "Emisor actualizado",
                    "es_cliente": "No",
                    "es_proveedor": "No",
                    "es_emisor": "Sí",
                }],
                sales=[self._sales(cuit_emisor="20888888888")],
            ),
        )

        self.assertFalse(result["ok"])
        self.assertEqual(self.tenant.cuit, "30111111111")
        self.assertEqual(self.issuer.cuit, "20111111111")
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)

    def test_duplicate_company_prevents_all_writes(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(
                companies=[{
                    "rowNumber": 2,
                    "cuit": self.client.cuit,
                    "razon_social": "Cliente repetido",
                    "es_cliente": "Sí",
                    "es_proveedor": "No",
                    "es_emisor": "No",
                }],
                sales=[self._sales()],
            ),
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["errors"][0]["sheet"], "Empresas")
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)
        self.assertEqual(self.session.query(models.Company).count(), 3)

    def test_any_validation_error_prevents_all_writes(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(
                sales=[self._sales()],
                collections=[self._collection(2, importe="100.01")],
            ),
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["errors"][0]["sheet"], "Cobros")
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)
        self.assertEqual(self.session.query(models.SalesCollection).count(), 0)

    def test_partial_settlements_preserve_partial_invoice_status(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(
                sales=[self._sales()],
                purchases=[self._purchase()],
                collections=[self._collection(2, importe="40.00")],
                payments=[self._payment(2, importe="40.00")],
            ),
        )

        self.assertTrue(result["ok"])
        self.assertEqual(self.session.query(models.SalesInvoice).one().estado, "parcial")
        self.assertEqual(self.session.query(models.PurchaseInvoice).one().estado, "parcial")

    def test_settlements_accumulate_against_existing_paid_balance(self):
        invoice = models.PurchaseInvoice(
            tenant_id=self.tenant.id,
            proveedor_id=self.supplier.id,
            letra="A",
            punto_venta=1,
            nro_factura=2,
            monto_total=Decimal("100.00"),
            estado="parcial",
        )
        self.session.add(invoice)
        self.session.flush()
        self.session.add(models.PurchasePayment(
            tenant_id=self.tenant.id,
            factura_compra_id=invoice.id,
            monto=Decimal("30.00"),
            fecha_pago=date(2026, 10, 1),
        ))
        self.session.commit()

        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(payments=[
                self._payment(2, importe="50.00"),
                self._payment(3, importe="21.00", comprobante="PAG-3"),
            ]),
        )

        self.assertFalse(result["ok"])
        self.assertEqual(self.session.query(models.PurchasePayment).count(), 1)
        self.assertEqual(invoice.estado, "parcial")

    def test_unknown_company_is_reported_without_creating_records(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(sales=[self._sales(cuit_cliente="20999999999")]),
        )

        self.assertFalse(result["ok"])
        self.assertIn("no está registrado", result["errors"][0]["message"])
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)

    def test_duplicate_invoice_is_rejected_without_writes(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(sales=[
                self._sales(2),
                self._sales(3, numero_factura=2),
            ]),
        )

        self.assertFalse(result["ok"])
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)

    def test_existing_receipt_cannot_be_imported_twice(self):
        invoice = models.SalesInvoice(
            tenant_id=self.tenant.id,
            emisor_id=self.issuer.id,
            cliente_id=self.client.id,
            letra="A",
            punto_venta=1,
            nro_factura=2,
            monto_total=Decimal("100.00"),
            estado="parcial",
        )
        self.session.add(invoice)
        self.session.flush()
        self.session.add(models.SalesCollection(
            tenant_id=self.tenant.id,
            factura_venta_id=invoice.id,
            monto=Decimal("30.00"),
            fecha_cobro=date(2026, 10, 15),
            nro_comprobante="COB-2",
        ))
        self.session.commit()

        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(collections=[
                self._collection(2, importe="30.00", comprobante="COB-2"),
            ]),
        )

        self.assertFalse(result["ok"])
        self.assertIn("repetido", result["errors"][0]["message"])
        self.assertEqual(self.session.query(models.SalesCollection).count(), 1)

    def test_amount_must_fit_the_invoice_decimal_precision(self):
        result = import_finance_rows(
            self.session,
            self.tenant.id,
            self._payload(sales=[self._sales(importe="1000000000000000")]),
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["errors"][0]["field"], "Importe")
        self.assertEqual(self.session.query(models.SalesInvoice).count(), 0)


if __name__ == "__main__":
    unittest.main()
