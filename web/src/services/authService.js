import { apiClient } from './apiClient';
import { AUTH_ROUTES, USERS_ROUTES } from '../routes/routes';

export const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  return apiClient.postForm('/auth/token', formData, { auth: false });
};

export const getCurrentUser = () => apiClient.get(USERS_ROUTES.me);
export const verifyEmail = (token) =>
  apiClient.post(AUTH_ROUTES.verifyEmail, { token }, { auth: false });
export const resendEmailVerification = (email) =>
  apiClient.post(AUTH_ROUTES.resendVerification, { email }, { auth: false });
export const requestPasswordReset = (email) =>
  apiClient.post(AUTH_ROUTES.forgotPassword, { email }, { auth: false });
export const resetPassword = (token, newPassword) =>
  apiClient.post(AUTH_ROUTES.resetPassword, { token, new_password: newPassword }, { auth: false });
export const resetPasswordWithRecoveryCode = (data) =>
  apiClient.post(AUTH_ROUTES.recoverWithCode, data, { auth: false });
