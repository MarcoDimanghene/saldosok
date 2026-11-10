import unittest
from types import SimpleNamespace

from fastapi import HTTPException

from back.models.user import User
from back.schemas.user import UserCreate, UserUpdate
from database.security import (
    create_access_token,
    get_current_superadmin,
    get_current_user,
)


class GetCurrentSuperadminTests(unittest.TestCase):
    def test_email_alone_does_not_grant_superadmin_access(self):
        user = SimpleNamespace(
            email="superadmin@saldook.com",
            is_superadmin=False,
        )

        with self.assertRaises(HTTPException) as error:
            get_current_superadmin(user)

        self.assertEqual(error.exception.status_code, 403)

    def test_explicit_superadmin_role_grants_access(self):
        user = SimpleNamespace(
            email="admin@example.com",
            is_superadmin=True,
        )

        self.assertIs(get_current_superadmin(user), user)

    def test_public_user_schemas_cannot_assign_superadmin_role(self):
        self.assertNotIn("is_superadmin", UserCreate.model_fields)
        self.assertNotIn("is_superadmin", UserUpdate.model_fields)

    def test_superadmin_role_defaults_to_false_and_is_required_in_database(self):
        role_column = User.__table__.c.is_superadmin

        self.assertFalse(role_column.nullable)
        self.assertFalse(role_column.default.arg)
        self.assertEqual(str(role_column.server_default.arg), "false")

    def test_malformed_subject_is_rejected_as_unauthorized(self):
        token = create_access_token({"sub": "not-a-user-id"})

        with self.assertRaises(HTTPException) as error:
            get_current_user(token, db=None)

        self.assertEqual(error.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
