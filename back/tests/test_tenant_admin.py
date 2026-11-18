import unittest
from types import SimpleNamespace

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models
from back.crud.tenants import create_tenant_with_admin
from back.crud.users import create_user
from back.routes.tenants import router as tenants_router, update_current_tenant
from back.routes.user import create_user_for_tenant, resend_user_invitation, update_user_password
from back.schemas.tenants import TenantRegister, TenantUpdate
from back.schemas.user import UserCreate, UserPasswordUpdate, UserUpdate
from database.database import Base, get_db
from database.security import get_current_tenant_admin, verify_password


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

    def test_tenant_registration_requires_superadmin_authentication(self):
        app = FastAPI()
        app.include_router(tenants_router)
        app.dependency_overrides[get_db] = lambda: self.session

        with TestClient(app) as client:
            response = client.post(
                "/tenants/register",
                json={
                    "nombre": "Administradora",
                    "dni": "30123456",
                    "username": "adminnueva",
                    "email": "admin@example.com",
                    "password": "secure-password",
                },
            )

        self.assertEqual(response.status_code, 401)

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

    def test_admin_can_create_members_with_a_password(self):
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
                password="member-secret",
            ),
            self.session,
            admin,
        )

        created = self.session.query(models.User).filter_by(
            username="integrante"
        ).one()
        self.assertEqual(result["user"], created)
        self.assertFalse(created.is_email_verified)
        self.assertTrue(created.hashed_password)
        self.assertIn("ya puede iniciar sesión", result["message"])
        self.assertTrue(verify_password("member-secret", created.hashed_password))

    def test_tenant_admin_can_change_a_user_password_without_exposing_it(self):
        tenant = models.Tenant()
        self.session.add(tenant)
        self.session.flush()
        admin = models.User(
            username="titular-cambiar-clave",
            email="titular-clave@example.com",
            hashed_password="admin-hash",
            tenant_id=tenant.id,
            is_tenant_admin=True,
        )
        member = models.User(
            username="miembro-cambiar-clave",
            email="miembro-clave@example.com",
            hashed_password="old-hash",
            tenant_id=tenant.id,
        )
        self.session.add_all([admin, member])
        self.session.commit()

        result = update_user_password(
            member.id,
            UserPasswordUpdate(password="new-member-secret"),
            self.session,
            admin,
        )

        self.assertEqual(result["message"], "La contraseña se actualizó correctamente.")
        self.assertTrue(verify_password("new-member-secret", member.hashed_password))
        self.assertNotIn("password", result)
        password_event = self.session.query(models.AuditLog).filter_by(
            entity_id=member.id,
            action="password_reset",
        ).one()
        self.assertEqual(password_event.after_data, {"password_changed": True})

    def test_admin_cannot_change_password_for_a_user_in_another_tenant(self):
        tenant = models.Tenant()
        another_tenant = models.Tenant()
        self.session.add_all([tenant, another_tenant])
        self.session.flush()
        admin = models.User(
            username="titular-clave-ajena",
            email="titular-ajeno@example.com",
            hashed_password="admin-hash",
            tenant_id=tenant.id,
            is_tenant_admin=True,
        )
        member = models.User(
            username="miembro-otro-tenant",
            email="miembro-otro@example.com",
            hashed_password="old-hash",
            tenant_id=another_tenant.id,
        )
        self.session.add_all([admin, member])
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            update_user_password(
                member.id,
                UserPasswordUpdate(password="new-member-secret"),
                self.session,
                admin,
            )

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(member.hashed_password, "old-hash")

    def test_invitation_sending_is_disabled(self):
        tenant = models.Tenant()
        self.session.add(tenant)
        self.session.flush()
        admin = models.User(
            username="titular-invitacion",
            email="titular-invitacion@example.com",
            hashed_password="hash",
            tenant_id=tenant.id,
            is_tenant_admin=True,
        )
        self.session.add(admin)
        self.session.commit()

        with self.assertRaises(HTTPException) as create_error:
            create_user_for_tenant(
                UserCreate(
                    nombre="Inactivo",
                    username="inactivo",
                    email="inactivo@example.com",
                    password="inactive-secret",
                    is_active=False,
                ),
                self.session,
                admin,
            )
        self.assertEqual(create_error.exception.status_code, 422)

        member = models.User(
            username="miembro-inactivo",
            email="miembro-inactivo@example.com",
            hashed_password="hash",
            tenant_id=tenant.id,
            is_active=False,
            is_email_verified=False,
        )
        self.session.add(member)
        self.session.commit()

        with self.assertRaises(HTTPException) as resend_error:
            resend_user_invitation(member.id, self.session, admin)

        self.assertEqual(resend_error.exception.status_code, 410)

    def test_invitation_sending_is_disabled_for_unverified_accounts(self):
        tenant = models.Tenant()
        self.session.add(tenant)
        self.session.flush()
        admin = models.User(
            username="titular-sin-correo",
            email="titular-sin-correo@example.com",
            hashed_password="hash",
            tenant_id=tenant.id,
            is_tenant_admin=True,
        )
        member = models.User(
            username="miembro-sin-correo",
            hashed_password="hash",
            tenant_id=tenant.id,
            is_email_verified=False,
        )
        self.session.add_all([admin, member])
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            resend_user_invitation(member.id, self.session, admin)

        self.assertEqual(error.exception.status_code, 410)

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
                    password="member-secret",
                ),
                self.session,
                admin,
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertIn("máximo de 10 usuarios", error.exception.detail)


if __name__ == "__main__":
    unittest.main()
