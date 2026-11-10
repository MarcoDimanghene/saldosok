import { getCompanies } from '../../services/companyService';
import {
  getPurchaseInvoices,
  getSalesInvoices,
} from '../../services/invoiceService';
import { getDashboardSummary } from '../../services/dashboardService';
import {
  COMPANIES_LOADED,
  DASHBOARD_LOADED,
  INVOICES_LOADED,
  LOAD_FAILED,
  LOAD_STARTED,
} from '../actionTypes';

const fetchResource = async ({
  dispatch,
  getState,
  key,
  selectStatus,
  request,
  onSuccess,
  force,
}) => {
  const sessionGeneration = getState().session.generation;
  const currentStatus = selectStatus(getState());
  if (currentStatus === 'loading' || (currentStatus === 'succeeded' && !force)) return;

  dispatch({ type: LOAD_STARTED, key });
  try {
    const result = await request();
    if (getState().session.generation === sessionGeneration) {
      dispatch(onSuccess(result));
    }
  } catch (error) {
    if (getState().session.generation === sessionGeneration) {
      dispatch({
        type: LOAD_FAILED,
        key,
        error: error.message || 'No se pudieron cargar los datos.',
      });
    }
  }
};

export const fetchCompanies = ({ force = false } = {}) => (dispatch, getState) => (
  fetchResource({
    dispatch,
    getState,
    key: 'companies',
    selectStatus: (state) => state.companies.status,
    request: getCompanies,
    onSuccess: (payload) => ({ type: COMPANIES_LOADED, payload }),
    force,
  })
);

export const fetchSalesInvoices = ({ force = false } = {}) => (dispatch, getState) => (
  fetchResource({
    dispatch,
    getState,
    key: 'salesInvoices',
    selectStatus: (state) => state.invoices.salesStatus,
    request: getSalesInvoices,
    onSuccess: (payload) => ({ type: INVOICES_LOADED, key: 'salesInvoices', payload }),
    force,
  })
);

export const fetchPurchaseInvoices = ({ force = false } = {}) => (dispatch, getState) => (
  fetchResource({
    dispatch,
    getState,
    key: 'purchaseInvoices',
    selectStatus: (state) => state.invoices.purchasesStatus,
    request: getPurchaseInvoices,
    onSuccess: (payload) => ({ type: INVOICES_LOADED, key: 'purchaseInvoices', payload }),
    force,
  })
);

export const fetchDashboard = ({ force = false } = {}) => (dispatch, getState) => (
  fetchResource({
    dispatch,
    getState,
    key: 'dashboard',
    selectStatus: (state) => state.dashboard.status,
    request: getDashboardSummary,
    onSuccess: (payload) => ({ type: DASHBOARD_LOADED, payload }),
    force,
  })
);
