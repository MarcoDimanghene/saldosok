import hashlib
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models
from back.routes.auth import login_for_access_token
from back.routes.tenants import register_tenant_with_user, verify_email
from back.schemas.tenants import TenantRegister
from back.schemas.user import EmailVerificationToken
from database.database import Base
from database.security import get_password_hash


class EmailVerificationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        tenant = models.Tenant(
            cuit="30111111111",
            razon_social="Organización",
            condicion_iva="Responsable Inscripto",
        )
        self.session.add(tenant)
        self.session.flush()
        self.user = models.User(
            nombre="Usuario",
            username="usuario",
            email="user@example.com",
            hashed_password=get_password_hash("secret"),
            tenant_id=tenant.id,
            is_email_verified=False,
        )
        self.session.add(self.user)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_unverified_user_can_login(self):
        form = SimpleNamespace(username=self.user.email, password="secret")
        result = login_for_access_token(form, self.session)
        self.assertEqual(result["token_type"], "bearer")
        self.assertTrue(result["access_token"])

    def test_verification_token_is_single_use(self):
        raw_token = "one-time-token"
        verification = models.EmailVerification(
            user_id=self.user.id,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        self.session.add(verification)
        self.session.commit()

        result = verify_email(EmailVerificationToken(token=raw_token), self.session)

        self.assertTrue(self.user.is_email_verified)
        self.assertEqual(
            result["message"],
            "Correo confirmado. Ya puedes recuperar tu contraseña por email.",
        )
        with self.assertRaises(HTTPException):
            verify_email(EmailVerificationToken(token=raw_token), self.session)

    def test_expired_token_cannot_verify_email(self):
        raw_token = "expired-token"
        verification = models.EmailVerification(
            user_id=self.user.id,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        self.session.add(verification)
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            verify_email(EmailVerificationToken(token=raw_token), self.session)

        self.assertEqual(error.exception.status_code, 400)
        self.assertFalse(self.user.is_email_verified)

    @patch("back.services.email_verification.send_verification_email")
    def test_registration_creates_user_first_and_sends_email_verification(self, send_email):
        registration = TenantRegister(
            nombre="Administradora",
            dni="30123456",
            username="adminnueva",
            email="admin@example.com",
            password="secret",
        )

        result = register_tenant_with_user(registration, self.session)

        created_user = self.session.query(models.User).filter_by(
            email="admin@example.com"
        ).one()
        tenant = self.session.query(models.Tenant).filter_by(
            id=created_user.tenant_id
        ).one()
        self.assertFalse(created_user.is_email_verified)
        self.assertEqual(created_user.dni, "30123456")
        self.assertIsNone(tenant.cuit)
        self.assertIsNone(tenant.razon_social)
        self.assertEqual(self.session.query(models.Company).count(), 0)
        send_email.assert_called_once()
        self.assertEqual(send_email.call_args.args[0], "admin@example.com")
        self.assertEqual(result["user"]["is_email_verified"], False)
        self.assertTrue(result["recovery_code"])

    def test_registration_requires_email(self):
        with self.assertRaises(ValidationError):
            TenantRegister(
                nombre="Administradora",
                username="admincorreo",
                password="secret",
            )


if __name__ == "__main__":
    unittest.main()
