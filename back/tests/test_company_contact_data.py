import unittest
from types import SimpleNamespace

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models, schemas
from back.crud.companies import create_company, update_company
from back.routes.companies import creteate_company, delete_company_route, update_company_route
from database.database import Base


class CompanyContactDataTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.tenant = models.Tenant(
            cuit="30111111111",
            razon_social="Organización de prueba",
            condicion_iva="Responsable Inscripto",
        )
        self.session.add(self.tenant)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_company_create_persists_contact_and_supplier_details(self):
        company = create_company(
            self.session,
            self.tenant.id,
            schemas.CompanyCreate(
                tax_id="20111111111",
                legal_name="Prestador de prueba",
                is_supplier=True,
                condicion_fiscal="Monotributo",
                banco="Banco Nación",
                cbu_cvu="1234567890123456789012",
                alias_cbu="PRESTADOR.ALIAS",
                titular_cuenta="Prestador de prueba",
                categoria_servicio="Mantenimiento",
                dias_credito=30,
                contacto_nombre="Contacto de prueba",
                email_1="contacto@example.com",
                telefono_1="1122334455",
                observaciones="Paga a 30 días",
            ),
        )

        self.assertEqual(company.condicion_iva, "Monotributo")
        self.assertEqual(company.condicion_fiscal, "Monotributo")
        self.assertEqual(company.cbu_cvu, "1234567890123456789012")
        self.assertEqual(company.dias_credito, 30)
        response = schemas.CompanyResponse.model_validate(company)
        self.assertEqual(response.email_1, "contacto@example.com")
        self.assertEqual(response.categoria_servicio, "Mantenimiento")

    def test_supplier_can_be_created_without_tax_id_and_with_location(self):
        company = create_company(
            self.session,
            self.tenant.id,
            schemas.CompanyCreate(
                legal_name="Proveedor sin identificación fiscal",
                is_supplier=True,
                localidad="Rosario",
                provincia="Santa Fe",
            ),
        )

        self.assertIsNone(company.cuit)
        self.assertEqual(company.localidad, "Rosario")
        self.assertEqual(company.provincia, "Santa Fe")
        response = schemas.CompanyResponse.model_validate(company)
        self.assertIsNone(response.cuit)
        self.assertEqual(response.provincia, "Santa Fe")

    def test_company_without_tax_id_must_be_supplier_only(self):
        with self.assertRaises(ValidationError):
            schemas.CompanyCreate(legal_name="Cliente sin identificación")

        with self.assertRaises(ValidationError):
            schemas.CompanyCreate(
                legal_name="Proveedor y cliente sin identificación",
                is_supplier=True,
                is_client=True,
            )

    def test_company_update_persists_issuer_and_client_details(self):
        company = create_company(
            self.session,
            self.tenant.id,
            schemas.CompanyCreate(
                tax_id="20222222222",
                legal_name="Empresa cliente",
                is_client=True,
                is_issuer=True,
            ),
        )

        updated = update_company(
            self.session,
            self.tenant.id,
            company.id,
            schemas.CompanyUpdate(
                banco_principal="Banco Provincia",
                cbu_propio="0001234567890123456789",
                alias_propio="EMPRESA.COBROS",
                localidad="La Plata",
                email_2="administracion@example.com",
                telefono_2="1144556677",
            ),
        )

        self.assertEqual(updated.banco_principal, "Banco Provincia")
        self.assertEqual(updated.alias_propio, "EMPRESA.COBROS")
        self.assertEqual(updated.localidad, "La Plata")
        self.assertEqual(updated.email_2, "administracion@example.com")
        self.assertEqual(updated.telefono_2, "1144556677")

    def test_company_defaults_credit_days_and_preserves_legacy_fields(self):
        company = create_company(
            self.session,
            self.tenant.id,
            schemas.CompanyCreate(
                tax_id="20333333333",
                legal_name="Empresa existente",
                tax_condition="Responsable Inscripto",
                is_client=True,
            ),
        )

        self.assertEqual(company.dias_credito, 0)
        self.assertEqual(company.condicion_iva, "Responsable Inscripto")
        self.assertIsNone(company.email_1)

    def test_credit_days_cannot_be_negative(self):
        with self.assertRaises(ValidationError):
            schemas.CompanyCreate(
                tax_id="20444444444",
                legal_name="Empresa inválida",
                dias_credito=-1,
            )

    def test_new_contact_fields_are_part_of_company_table(self):
        expected = {
            "banco_principal",
            "cbu_propio",
            "alias_propio",
            "localidad",
            "provincia",
            "banco",
            "cbu_cvu",
            "alias_cbu",
            "titular_cuenta",
            "categoria_servicio",
            "dias_credito",
            "contacto_nombre",
            "email_1",
            "email_2",
            "telefono_1",
            "telefono_2",
            "observaciones",
        }

        self.assertTrue(expected.issubset(models.Company.__table__.columns.keys()))

    def test_company_cuit_can_be_registered_in_separate_tenants(self):
        another_tenant = models.Tenant(
            cuit="30222222222",
            razon_social="Otra organización",
            condicion_iva="Responsable Inscripto",
        )
        self.session.add(another_tenant)
        self.session.flush()
        for tenant_id, name in (
            (self.tenant.id, "Empresa contraparte"),
            (another_tenant.id, "Empresa contraparte"),
        ):
            create_company(
                self.session,
                tenant_id,
                schemas.CompanyCreate(
                    tax_id="20111111111",
                    legal_name=name,
                    is_client=True,
                ),
            )

        self.assertEqual(
            self.session.query(models.Company)
            .filter(models.Company.cuit == "20111111111")
            .count(),
            2,
        )

    def test_issuer_is_only_managed_from_organization_profile(self):
        issuer = models.Company(
            cuit=self.tenant.cuit,
            razon_social=self.tenant.razon_social,
            es_emisor=True,
            tenant_id=self.tenant.id,
        )
        self.session.add(issuer)
        self.session.commit()
        user = SimpleNamespace(tenant_id=self.tenant.id)

        with self.assertRaises(HTTPException) as create_error:
            creteate_company(
                schemas.CompanyCreate(
                    tax_id="20333333333",
                    legal_name="Emisor manual",
                    is_issuer=True,
                ),
                self.session,
                user,
            )
        self.assertEqual(create_error.exception.status_code, 400)

        with self.assertRaises(HTTPException) as update_error:
            update_company_route(
                issuer.id,
                schemas.CompanyUpdate(legal_name="Nombre editado"),
                self.session,
                user,
            )
        self.assertEqual(update_error.exception.status_code, 400)

        with self.assertRaises(HTTPException) as delete_error:
            delete_company_route(issuer.id, self.session, user)
        self.assertEqual(delete_error.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
