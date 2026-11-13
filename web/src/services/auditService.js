import { apiClient } from './apiClient';
import { AUDIT_ROUTES } from '../routes/routes';

export const getAuditLogs = ({ skip = 0, limit = 100 } = {}) => (
  apiClient.get(`${AUDIT_ROUTES.list}?skip=${skip}&limit=${limit}`)
);
