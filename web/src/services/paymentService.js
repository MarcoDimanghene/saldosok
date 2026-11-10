import { apiClient } from './apiClient';
import { PAYMENTS_ROUTES } from '../routes/routes';

export const createCollection = (collection) =>
  apiClient.post(PAYMENTS_ROUTES.collectionsCreate, collection);
export const createPayment = (payment) =>
  apiClient.post(PAYMENTS_ROUTES.paymentsCreate, payment);
