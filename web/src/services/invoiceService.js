import { apiClient } from './apiClient';
import { INVOICES_ROUTES } from '../routes/routes';

export const getSalesInvoices = () => apiClient.get(INVOICES_ROUTES.salesList);
export const createSalesInvoice = (invoice) => apiClient.post(INVOICES_ROUTES.salesCreate, invoice);
export const getPurchaseInvoices = () => apiClient.get(INVOICES_ROUTES.purchaseList);
export const createPurchaseInvoice = (invoice) => apiClient.post(INVOICES_ROUTES.purchaseCreate, invoice);
export const createPendingPurchase = (purchase) =>
  apiClient.post(INVOICES_ROUTES.purchasePendingCreate, purchase);
export const completePendingPurchase = (invoiceId, invoice) =>
  apiClient.put(INVOICES_ROUTES.purchaseComplete(invoiceId), invoice);
export const updatePurchaseInvoice = (invoiceId, invoice) =>
  apiClient.patch(INVOICES_ROUTES.purchaseUpdate(invoiceId), invoice);
