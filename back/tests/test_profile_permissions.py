import unittest
from types import SimpleNamespace

from fastapi import HTTPException

from back import schemas
from back.routes.companies import _validate_company_creation
from back.routes.invoices import router as invoices_router
from back.routes.payments import router as payments_router
from back.routes.user import router as users_router
from database.security import (
    get_current_purchase_user,
    get_current_sales_user,
    get_current_tenant_admin,
    get_current_tenant_admin_or_analyst,
)


class ProfilePermissionTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(
            id=1,
            tenant_id=1,
            perfil="venta",
            is_tenant_admin=False,
        )

    @staticmethod
    def _route_dependency(router, path, dependency):
        route = next(route for route in router.routes if route.path == path)
        return any(item.call is dependency for item in route.dependant.dependencies)

    def test_invoice_and_payment_routes_require_the_matching_profile(self):
        self.assertTrue(
            self._route_dependency(
                invoices_router, "/invoices/sales/list", get_current_sales_user
            )
        )
        self.assertTrue(
            self._route_dependency(
                invoices_router, "/invoices/purchase/list", get_current_purchase_user
            )
        )
        self.assertTrue(
            self._route_dependency(
                invoices_router,
                "/invoices/operating-results/list",
                get_current_tenant_admin_or_analyst,
            )
        )
        self.assertTrue(
            self._route_dependency(
                users_router, "/users/", get_current_tenant_admin
            )
        )
        self.assertTrue(
            self._route_dependency(
                payments_router, "/payments/collection/invoice/{invoice_id}",
                get_current_sales_user,
            )
        )
        self.assertTrue(
            self._route_dependency(
                payments_router, "/payments/payment/invoice/{invoice_id}",
                get_current_purchase_user,
            )
        )

    def test_profile_guards_allow_only_matching_users_and_admin(self):
        self.assertIs(get_current_sales_user(self.user), self.user)
        with self.assertRaises(HTTPException):
            get_current_purchase_user(self.user)
        with self.assertRaises(HTTPException):
            get_current_tenant_admin(self.user)

        self.user.perfil = "compra"
        self.assertIs(get_current_purchase_user(self.user), self.user)
        with self.assertRaises(HTTPException):
            get_current_sales_user(self.user)

        self.user.is_tenant_admin = True
        self.assertIs(get_current_sales_user(self.user), self.user)
        self.assertIs(get_current_purchase_user(self.user), self.user)
        self.assertIs(get_current_tenant_admin(self.user), self.user)

    def test_analyst_profile_has_full_module_access_but_not_user_management(self):
        self.user.perfil = "analista"

        self.assertIs(get_current_sales_user(self.user), self.user)
        self.assertIs(get_current_purchase_user(self.user), self.user)
        self.assertIs(get_current_tenant_admin_or_analyst(self.user), self.user)
        with self.assertRaises(HTTPException):
            get_current_tenant_admin(self.user)

        self.assertTrue(
            self._route_dependency(
                users_router, "/users/", get_current_tenant_admin
            )
        )

    def test_sales_and_purchase_profiles_can_create_only_their_company_type(self):
        customer = schemas.CompanyCreate(
            legal_name="Cliente de prueba",
            tax_id="20111111111",
            is_client=True,
        )
        supplier = schemas.CompanyCreate(
            legal_name="Proveedor de prueba",
            tax_id="20222222222",
            is_supplier=True,
        )

        _validate_company_creation(customer, self.user)
        with self.assertRaises(HTTPException):
            _validate_company_creation(supplier, self.user)

        self.user.perfil = "compra"
        _validate_company_creation(supplier, self.user)
        with self.assertRaises(HTTPException):
            _validate_company_creation(customer, self.user)

        self.user.perfil = "analista"
        _validate_company_creation(customer, self.user)
        _validate_company_creation(supplier, self.user)

    def test_user_schemas_accept_the_analyst_profile(self):
        user = schemas.UserCreate(
            nombre="Usuario Analista",
            username="usuario.analista",
            email="analista@example.com",
            perfil="analista",
        )

        self.assertEqual(user.perfil, "analista")
