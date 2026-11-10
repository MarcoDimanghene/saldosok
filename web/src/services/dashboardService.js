import { apiClient } from './apiClient';
import { DASHBOARD_ROUTES } from '../routes/routes';

export const getDashboardSummary = () => apiClient.get(DASHBOARD_ROUTES.summary);
