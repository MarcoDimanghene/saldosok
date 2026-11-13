import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import {
  AUTH_ROUTES,
  AUDIT_ROUTES,
  COMPANIES_ROUTES,
  DASHBOARD_ROUTES,
  INVOICES_ROUTES,
  IMPORTS_ROUTES,
  PAYMENTS_ROUTES,
  ROUTE_MAP,
  TENANTS_ROUTES,
  USERS_ROUTES,
} from '../src/routes/routes.js';

test('Vercel rewrites SPA routes to the frontend entry point', async () => {
  const config = JSON.parse(
    await readFile(new URL('../vercel.json', import.meta.url), 'utf8'),
  );
  assert.deepEqual(config.rewrites, [
    { source: '/(.*)', destination: '/index.html' },
  ]);
});

test('navigation paths match the routes rendered by AppRoutes', () => {
  assert.deepEqual(ROUTE_MAP, {
    root: '/',
    login: '/login',
    dashboard: '/dashboard',
    users: '/users',
    companies: '/companies',
    invoices: '/invoices',
    imports: '/imports',
    reports: '/reports',
    audit: '/audit',
  });
});

test('API endpoint paths match the FastAPI routers', () => {
  assert.deepEqual(AUTH_ROUTES, {
    login: '/auth/token',
    verifyEmail: '/tenants/verify-email',
    resendVerification: '/tenants/resend-verification',
    forgotPassword: '/auth/forgot-password',
    resetPassword: '/auth/reset-password',
    recoverWithCode: '/auth/recover-with-code',
  });
  assert.deepEqual(DASHBOARD_ROUTES, { summary: '/dashboard/summary' });
  assert.deepEqual(IMPORTS_ROUTES, { finance: '/imports/finance' });
  assert.deepEqual(AUDIT_ROUTES, { list: '/audit/' });

  assert.deepEqual(
    {
      list: COMPANIES_ROUTES.list,
      create: COMPANIES_ROUTES.create,
      byCuit: COMPANIES_ROUTES.byCuit('20-123/456'),
      search: COMPANIES_ROUTES.search,
      update: COMPANIES_ROUTES.update(12),
      delete: COMPANIES_ROUTES.delete(12),
    },
    {
      list: '/companies/',
      create: '/companies/',
      byCuit: '/companies/cuit/20-123%2F456',
      search: '/companies/search',
      update: '/companies/12',
      delete: '/companies/12',
    }
  );

  assert.deepEqual(
    {
      list: USERS_ROUTES.list,
      create: USERS_ROUTES.create,
      me: USERS_ROUTES.me,
      byId: USERS_ROUTES.byId(7),
      invitation: USERS_ROUTES.invitation(7),
      update: USERS_ROUTES.update(7),
      delete: USERS_ROUTES.delete(7),
    },
    {
      list: '/users/',
      create: '/users/',
      me: '/users/me',
      byId: '/users/7',
      invitation: '/users/7/invitation',
      update: '/users/7',
      delete: '/users/7',
    }
  );

  assert.deepEqual(TENANTS_ROUTES, {
    list: '/tenants/',
    create: '/tenants/',
    me: '/tenants/me',
    update: '/tenants/me',
  });

  assert.deepEqual(
    {
      extract: INVOICES_ROUTES.extract,
      salesList: INVOICES_ROUTES.salesList,
      salesSearch: INVOICES_ROUTES.salesSearch,
      salesCreate: INVOICES_ROUTES.salesCreate,
      salesUpdate: INVOICES_ROUTES.salesUpdate(18),
      purchaseList: INVOICES_ROUTES.purchaseList,
      purchaseSearch: INVOICES_ROUTES.purchaseSearch,
      purchaseCreate: INVOICES_ROUTES.purchaseCreate,
      purchasePendingCreate: INVOICES_ROUTES.purchasePendingCreate,
      purchaseComplete: INVOICES_ROUTES.purchaseComplete(20),
      purchaseUpdate: INVOICES_ROUTES.purchaseUpdate(19),
    },
    {
      extract: '/invoices/extract',
      salesList: '/invoices/sales/list',
      salesSearch: '/invoices/sales/search-number',
      salesCreate: '/invoices/sales',
      salesUpdate: '/invoices/sales/18',
      purchaseList: '/invoices/purchase/list',
      purchaseSearch: '/invoices/purchase/search-number',
      purchaseCreate: '/invoices/purchase',
      purchasePendingCreate: '/invoices/purchase/pending',
      purchaseComplete: '/invoices/purchase/20/formal-invoice',
      purchaseUpdate: '/invoices/purchase/19',
    }
  );

  assert.deepEqual(
    {
      collectionsList: PAYMENTS_ROUTES.collectionsList(5),
      collectionsCreate: PAYMENTS_ROUTES.collectionsCreate,
      collectionsUpdate: PAYMENTS_ROUTES.collectionsUpdate(6),
      collectionsDelete: PAYMENTS_ROUTES.collectionsDelete(6),
      paymentsList: PAYMENTS_ROUTES.paymentsList(8),
      paymentsCreate: PAYMENTS_ROUTES.paymentsCreate,
      paymentsUpdate: PAYMENTS_ROUTES.paymentsUpdate(9),
      paymentsDelete: PAYMENTS_ROUTES.paymentsDelete(9),
    },
    {
      collectionsList: '/payments/collection/invoice/5',
      collectionsCreate: '/payments/collection',
      collectionsUpdate: '/payments/collection/6',
      collectionsDelete: '/payments/collection/6',
      paymentsList: '/payments/payment/invoice/8',
      paymentsCreate: '/payments/payment',
      paymentsUpdate: '/payments/payment/9',
      paymentsDelete: '/payments/payment/9',
    }
  );
});
