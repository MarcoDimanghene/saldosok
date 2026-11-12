import { apiClient } from './apiClient';

export const getMyTenant = () => apiClient.get('/tenants/me');

export const updateMyTenant = (data) => apiClient.patch('/tenants/me', data);
