import { combineReducers } from 'redux';
import companies from './companiesReducer.js';
import invoices from './invoicesReducer.js';
import dashboard from './dashboardReducer.js';
import session from './sessionReducer.js';

const rootReducer = combineReducers({
  companies,
  invoices,
  dashboard,
  session,
});

export default rootReducer;
