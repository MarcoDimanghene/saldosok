import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models
from back.crud.tenants import create_tenant_with_admin
from back.crud.users import create_user
from back.routes.tenants import update_current_tenant
from back.routes.user import create_user_for_tenant
from back.schemas.tenants import TenantRegister, TenantUpdate
from back.schemas.user import UserCreate, UserUpdate
from database.database import Base
from database.security import get_current_tenant_admin


class TenantAdminTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_regular_user_is_denied_admin_access(self):
        user = SimpleNamespace(is_tenant_admin=False)

        with self.assertRaises(HTTPException) as error:
            get_current_tenant_admin(user)

        self.assertEqual(error.exception.status_code, 403)

    def test_tenant_admin_is_allowed(self):
        user = SimpleNamespace(is_tenant_admin=True)

        self.assertIs(get_current_tenant_admin(user), user)

    def test_public_user_schemas_cannot_assign_admin_roles(self):
        self.assertNotIn("is_tenant_admin", UserCreate.model_fields)
        self.assertNotIn("is_tenant_admin", UserUpdate.model_fields)
        self.assertNotIn("is_superadmin", UserCreate.model_fields)
        self.assertNotIn("is_superadmin", UserUpdate.model_fields)

    def test_registration_makes_creator_admin_and_new_users_regular(self):
        registration = TenantRegister(
            nombre="Admin inicial",
            dni="30123456",
            username="admininicial",
            email="admin@example.com",
            password="secure-password",
        )
        tenant, owner = create_tenant_with_admin(
            self.session,
            registration,
            hashed_password="hashed-password",
        )

        self.assertTrue(owner.is_tenant_admin)
        self.assertEqual(owner.dni, "30123456")
        self.assertIsNone(tenant.cuit)
        self.assertEqual(self.session.query(models.Company).count(), 0)
        regular_user = create_user(
            self.session,
            tenant.id,
            UserCreate(
                nombre="Usuario",
                username="usuarioequipo",
                email="user@example.com",
                password="secure-password",
            ),
            hashed_password="hashed-password",
        )
        self.assertFalse(regular_user.is_tenant_admin)
        self.assertFalse(regular_user.is_superadmin)

    def test_user_role_columns_default_to_non_admin(self):
        self.assertFalse(models.User.__table__.c.is_tenant_admin.default.arg)
        self.assertFalse(models.User.__table__.c.is_superadmin.default.arg)

    def test_account_admin_profile_changes_do_not_create_or_modify_issuers(self):
        tenant = models.Tenant()
        self.session.add(tenant)
        self.session.commit()
        user = SimpleNamespace(tenant_id=tenant.id, is_tenant_admin=True)

        updated = update_current_tenant(
            TenantUpdate(
                cuit="30111111111",
                razon_social="Organización",
                condicion_iva="Responsable Inscripto",
            ),
            self.session,
            user,
        )

        self.assertEqual(updated.cuit, "30111111111")
        self.assertEqual(
            self.session.query(models.Company).filter_by(
                tenant_id=tenant.id,
                es_emisor=True,
            ).count(),
            0,
        )

        issuer = models.Company(
            tenant_id=tenant.id,
            cuit="20111111111",
            razon_social="Emisor independiente",
            es_emisor=True,
        )
        self.session.add(issuer)
        self.session.commit()

        update_current_tenant(
            TenantUpdate(
                cuit="30122222222",
                razon_social="Organización actualizada",
            ),
            self.session,
            user,
        )
        self.session.refresh(issuer)
        self.assertEqual(issuer.cuit, "20111111111")
        self.assertEqual(issuer.razon_social, "Emisor independiente")

    @patch("back.routes.user.issue_email_verification")
    def test_admin_can_create_individual_member_accounts_with_unique_email(self, verify_email):
        tenant = models.Tenant()
        self.session.add(tenant)
        self.session.flush()
        admin = models.User(
            nombre="Titular",
            username="titular-equipo",
            email="titular@example.com",
            hashed_password="hash",
            tenant_id=tenant.id,
            is_tenant_admin=True,
        )
        self.session.add(admin)
        self.session.commit()

        result = create_user_for_tenant(
            UserCreate(
                nombre="Integrante",
                username="integrante",
                email="integrante@example.com",
                password="password",
            ),
            self.session,
            admin,
        )

        created = self.session.query(models.User).filter_by(
            username="integrante"
        ).one()
        self.assertEqual(result["user"], created)
        self.assertIn("confirmar su correo", result["message"])
        verify_email.assert_called_once_with(self.session, created)

    def test_tenant_maximum_is_ten_users_including_the_owner(self):
        tenant = models.Tenant()
        self.session.add(tenant)
        self.session.flush()
        admin = models.User(
            username="titular-limite",
            email="titular-limite@example.com",
            hashed_password="hash",
            tenant_id=tenant.id,
            is_tenant_admin=True,
        )
        members = [
            models.User(
                username=f"miembro{index}",
                email=f"miembro{index}@example.com",
                hashed_password="hash",
                tenant_id=tenant.id,
            )
            for index in range(9)
        ]
        self.session.add_all([admin, *members])
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            create_user_for_tenant(
                UserCreate(
                    nombre="Integrante",
                    username="integrante-limite",
                    email="integrante-limite@example.com",
                    password="password",
                ),
                self.session,
                admin,
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertIn("máximo de 10 usuarios", error.exception.detail)


if __name__ == "__main__":
    unittest.main()
