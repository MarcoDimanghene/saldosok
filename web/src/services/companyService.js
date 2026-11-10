import { apiClient } from './apiClient';
import { COMPANIES_ROUTES } from '../routes/routes';

export const getCompanies = () => apiClient.get(COMPANIES_ROUTES.list);
export const createCompany = (company) => apiClient.post(COMPANIES_ROUTES.create, company);
export const updateCompany = (companyId, company) =>
  apiClient.patch(COMPANIES_ROUTES.update(companyId), company);
