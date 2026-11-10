import { apiClient } from './apiClient';

export const registerTenant = (data) =>
  apiClient.post('/tenants/register', data, { auth: false });

export const getMyTenant = () => apiClient.get('/tenants/me');

export const updateMyTenant = (data) => apiClient.patch('/tenants/me', data);
