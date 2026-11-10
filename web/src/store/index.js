import { applyMiddleware, createStore } from 'redux';
import rootReducer from './reducers';
import { CLEAR_FINANCE } from './actionTypes';

const thunkMiddleware = ({ dispatch, getState }) => (next) => (action) => (
  typeof action === 'function' ? action(dispatch, getState) : next(action)
);

export const store = createStore(rootReducer, applyMiddleware(thunkMiddleware));
export const clearFinance = () => ({ type: CLEAR_FINANCE });
export {
  fetchCompanies,
  fetchDashboard,
  fetchPurchaseInvoices,
  fetchSalesInvoices,
} from './actions/financeActions';
