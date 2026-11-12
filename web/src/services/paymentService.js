import { apiClient } from './apiClient';
import { PAYMENTS_ROUTES } from '../routes/routes';

export const createCollection = (collection) =>
  apiClient.post(PAYMENTS_ROUTES.collectionsCreate, collection);
export const getCollectionsByInvoiceId = (invoiceId) =>
  apiClient.get(PAYMENTS_ROUTES.collectionsList(invoiceId));
export const updateCollection = (collectionId, collection) =>
  apiClient.put(PAYMENTS_ROUTES.collectionsUpdate(collectionId), collection);
export const createPayment = (payment) =>
  apiClient.post(PAYMENTS_ROUTES.paymentsCreate, payment);
export const getPaymentsByInvoiceId = (invoiceId) =>
  apiClient.get(PAYMENTS_ROUTES.paymentsList(invoiceId));
export const updatePayment = (paymentId, payment) =>
  apiClient.put(PAYMENTS_ROUTES.paymentsUpdate(paymentId), payment);
