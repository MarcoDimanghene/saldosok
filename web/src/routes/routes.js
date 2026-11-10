export const AUTH_ROUTES = {
  login: '/auth/token',
  verifyEmail: '/tenants/verify-email',
  resendVerification: '/tenants/resend-verification',
  forgotPassword: '/auth/forgot-password',
  resetPassword: '/auth/reset-password',
  recoverWithCode: '/auth/recover-with-code',
};

export const DASHBOARD_ROUTES = {
  summary: '/dashboard/summary',
};

export const COMPANIES_ROUTES = {
  list: '/companies/',
  create: '/companies/',
  byCuit: (taxId) => `/companies/cuit/${encodeURIComponent(taxId)}`,
  search: '/companies/search',
  update: (companyId) => `/companies/${companyId}`,
  delete: (companyId) => `/companies/${companyId}`,
};

export const USERS_ROUTES = {
  list: '/users/',
  create: '/users/',
  me: '/users/me',
  byId: (userId) => `/users/${userId}`,
  update: (userId) => `/users/${userId}`,
  delete: (userId) => `/users/${userId}`,
};

export const TENANTS_ROUTES = {
  register: '/tenants/register',
  list: '/tenants/',
  create: '/tenants/',
  me: '/tenants/me',
  update: '/tenants/me',
};

export const INVOICES_ROUTES = {
  extract: '/invoices/extract',
  salesList: '/invoices/sales/list',
  salesSearch: '/invoices/sales/search-number',
  salesCreate: '/invoices/sales',
  salesUpdate: (invoiceId) => `/invoices/sales/${invoiceId}`,
  purchaseList: '/invoices/purchase/list',
  purchaseSearch: '/invoices/purchase/search-number',
  purchaseCreate: '/invoices/purchase',
  purchasePendingCreate: '/invoices/purchase/pending',
  purchaseComplete: (invoiceId) => `/invoices/purchase/${invoiceId}/formal-invoice`,
  purchaseUpdate: (invoiceId) => `/invoices/purchase/${invoiceId}`,
};

export const PAYMENTS_ROUTES = {
  collectionsList: (invoiceId) => `/payments/collection/invoice/${invoiceId}`,
  collectionsCreate: '/payments/collection',
  collectionsUpdate: (collectionId) => `/payments/collection/${collectionId}`,
  collectionsDelete: (collectionId) => `/payments/collection/${collectionId}`,
  paymentsList: (invoiceId) => `/payments/payment/invoice/${invoiceId}`,
  paymentsCreate: '/payments/payment',
  paymentsUpdate: (paymentId) => `/payments/payment/${paymentId}`,
  paymentsDelete: (paymentId) => `/payments/payment/${paymentId}`,
};

export const IMPORTS_ROUTES = {
  finance: '/imports/finance',
};

export const ROUTE_MAP = {
  root: '/',
  login: '/login',
  register: '/register',
  plans: '/plans',
  dashboard: '/dashboard',
  users: '/users',
  companies: '/companies',
  invoices: '/invoices',
  imports: '/imports',
  reports: '/reports',
};

export default {
  AUTH_ROUTES,
  DASHBOARD_ROUTES,
  COMPANIES_ROUTES,
  USERS_ROUTES,
  TENANTS_ROUTES,
  INVOICES_ROUTES,
  PAYMENTS_ROUTES,
  IMPORTS_ROUTES,
  ROUTE_MAP,
};
