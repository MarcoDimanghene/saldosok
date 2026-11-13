import hashlib
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from back import models
from back.routes.auth import (
    request_password_reset,
    reset_password,
    reset_password_with_recovery_code,
)
from back.services.user_invitation import issue_user_invitation
from back.schemas.user import (
    PasswordResetRequest,
    PasswordResetToken,
    RecoveryCodePasswordReset,
)
from database.database import Base
from database.security import get_password_hash, verify_password


class PasswordRecoveryTests(unittest.TestCase):
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
            nombre="Admin",
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("old-secret"),
            is_tenant_admin=True,
            is_email_verified=True,
            tenant_id=tenant.id,
        )
        self.session.add(self.user)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    @patch("back.routes.auth.send_password_reset_email")
    def test_verified_email_can_reset_password_with_single_use_link(self, send_email):
        request_password_reset(PasswordResetRequest(email="admin@example.com"), self.session)
        raw_token = send_email.call_args.args[1]

        result = reset_password(
            PasswordResetToken(token=raw_token, new_password="new-secret"),
            self.session,
        )

        self.assertEqual(result["message"], "La contraseña se restableció correctamente.")
        self.assertTrue(verify_password("new-secret", self.user.hashed_password))
        with self.assertRaises(HTTPException):
            reset_password(
                PasswordResetToken(token=raw_token, new_password="other-secret"),
                self.session,
            )

    def test_unconfirmed_email_does_not_issue_reset_link(self):
        self.user.is_email_verified = False
        self.session.commit()

        with patch("back.routes.auth.send_password_reset_email") as send_email:
            result = request_password_reset(
                PasswordResetRequest(email="admin@example.com"),
                self.session,
            )

        send_email.assert_not_called()
        self.assertIn("Si la cuenta", result["message"])

    def test_recovery_code_is_single_use_and_only_resets_admin_account(self):
        raw_code = "single-use-recovery-code"
        self.session.add(models.PasswordRecoveryCode(
            user_id=self.user.id,
            code_hash=hashlib.sha256(raw_code.encode()).hexdigest(),
        ))
        self.session.commit()

        result = reset_password_with_recovery_code(
            RecoveryCodePasswordReset(
                username="admin",
                recovery_code=raw_code,
                new_password="recovered-secret",
            ),
            self.session,
        )

        self.assertIn("anterior ya no sirve", result["message"])
        self.assertTrue(result["recovery_code"])
        self.assertTrue(verify_password("recovered-secret", self.user.hashed_password))
        with self.assertRaises(HTTPException):
            reset_password_with_recovery_code(
                RecoveryCodePasswordReset(
                    username="admin",
                    recovery_code=raw_code,
                    new_password="other-secret",
                ),
                self.session,
            )
        next_result = reset_password_with_recovery_code(
            RecoveryCodePasswordReset(
                username="admin",
                recovery_code=result["recovery_code"],
                new_password="next-secret",
            ),
            self.session,
        )
        self.assertTrue(next_result["recovery_code"])

    def test_expired_reset_token_is_rejected(self):
        raw_token = "expired-reset-token"
        self.session.add(models.PasswordReset(
            user_id=self.user.id,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        ))
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            reset_password(
                PasswordResetToken(token=raw_token, new_password="new-secret"),
                self.session,
            )

        self.assertEqual(error.exception.status_code, 400)

    @patch("back.services.user_invitation.send_user_invitation_email")
    def test_invitation_link_sets_password_and_confirms_email_once(self, send_invitation):
        self.user.is_email_verified = False
        self.session.commit()

        issue_user_invitation(self.session, self.user)
        raw_token = send_invitation.call_args.args[1]

        reset_password(
            PasswordResetToken(token=raw_token, new_password="invite-password"),
            self.session,
        )

        self.assertTrue(self.user.is_email_verified)
        self.assertTrue(verify_password("invite-password", self.user.hashed_password))
        with self.assertRaises(HTTPException):
            reset_password(
                PasswordResetToken(token=raw_token, new_password="other-password"),
                self.session,
            )

    @patch(
        "back.services.user_invitation.send_user_invitation_email",
        side_effect=RuntimeError("SMTP is not configured"),
    )
    def test_invitation_email_failure_is_explicit_and_keeps_account_recoverable(self, send_invitation):
        self.user.is_email_verified = False
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            issue_user_invitation(self.session, self.user)

        self.assertEqual(error.exception.status_code, 503)
        self.assertIn("volver a enviarla", error.exception.detail)
        self.assertIsNotNone(
            self.session.query(models.PasswordReset).filter_by(user_id=self.user.id).first()
        )
        send_invitation.assert_called_once()


if __name__ == "__main__":
    unittest.main()
