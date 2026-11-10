import { apiClient } from './apiClient';
import { IMPORTS_ROUTES } from '../routes/routes';

export const importFinance = (data) => apiClient.post(IMPORTS_ROUTES.finance, data);
