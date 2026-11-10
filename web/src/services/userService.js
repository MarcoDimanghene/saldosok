import { apiClient } from './apiClient';
import { USERS_ROUTES } from '../routes/routes';

export const getUsers = () => apiClient.get(USERS_ROUTES.list);

export const createUser = (user) => apiClient.post(USERS_ROUTES.create, user);

export const updateUser = (userId, updates) =>
  apiClient.patch(USERS_ROUTES.update(userId), updates);

export const deleteUser = (userId) => apiClient.delete(USERS_ROUTES.delete(userId));
