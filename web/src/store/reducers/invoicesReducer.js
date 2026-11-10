import {
  CLEAR_FINANCE,
  INVOICES_LOADED,
  LOAD_FAILED,
  LOAD_STARTED,
} from '../actionTypes.js';

const initialState = {
  sales: [],
  purchases: [],
  salesStatus: 'idle',
  purchasesStatus: 'idle',
  salesError: null,
  purchasesError: null,
};

export default function invoicesReducer(state = initialState, action) {
  switch (action.type) {
    case LOAD_STARTED:
      if (action.key === 'salesInvoices') {
        return { ...state, salesStatus: 'loading', salesError: null };
      }
      if (action.key === 'purchaseInvoices') {
        return { ...state, purchasesStatus: 'loading', purchasesError: null };
      }
      return state;
    case INVOICES_LOADED:
      return action.key === 'salesInvoices'
        ? { ...state, sales: action.payload, salesStatus: 'succeeded', salesError: null }
        : {
          ...state,
          purchases: action.payload,
          purchasesStatus: 'succeeded',
          purchasesError: null,
        };
    case LOAD_FAILED:
      if (action.key === 'salesInvoices') {
        return { ...state, salesStatus: 'failed', salesError: action.error };
      }
      if (action.key === 'purchaseInvoices') {
        return { ...state, purchasesStatus: 'failed', purchasesError: action.error };
      }
      return state;
    case CLEAR_FINANCE:
      return initialState;
    default:
      return state;
  }
}
