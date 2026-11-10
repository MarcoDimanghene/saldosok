import assert from 'node:assert/strict';
import test from 'node:test';
import rootReducer from '../src/store/reducers/index.js';
import {
  CLEAR_FINANCE,
  COMPANIES_LOADED,
  DASHBOARD_LOADED,
  INVOICES_LOADED,
  LOAD_FAILED,
  LOAD_STARTED,
} from '../src/store/actionTypes.js';

test('finance reducers keep shared resources and their loading state', () => {
  let state = rootReducer(undefined, { type: '@@init' });

  state = rootReducer(state, { type: LOAD_STARTED, key: 'companies' });
  assert.equal(state.companies.status, 'loading');
  state = rootReducer(state, {
    type: COMPANIES_LOADED,
    payload: [{ id: 7, razon_social: 'Empresa' }],
  });
  assert.equal(state.companies.status, 'succeeded');
  assert.equal(state.companies.items[0].id, 7);

  state = rootReducer(state, { type: LOAD_STARTED, key: 'salesInvoices' });
  state = rootReducer(state, {
    type: INVOICES_LOADED,
    key: 'salesInvoices',
    payload: [{ id: 11 }],
  });
  assert.equal(state.invoices.sales[0].id, 11);
  assert.equal(state.invoices.salesStatus, 'succeeded');

  state = rootReducer(state, { type: LOAD_STARTED, key: 'dashboard' });
  state = rootReducer(state, {
    type: DASHBOARD_LOADED,
    payload: { accounts_receivable: '120.00' },
  });
  assert.equal(state.dashboard.summary.accounts_receivable, '120.00');
  assert.equal(state.dashboard.status, 'succeeded');
});

test('finance reducers surface loading errors and clear tenant-scoped data', () => {
  let state = rootReducer(undefined, { type: '@@init' });
  state = rootReducer(state, {
    type: LOAD_FAILED,
    key: 'purchaseInvoices',
    error: 'No se pudieron cargar las compras.',
  });
  assert.equal(state.invoices.purchasesStatus, 'failed');
  assert.equal(state.invoices.purchasesError, 'No se pudieron cargar las compras.');

  state = rootReducer(state, {
    type: COMPANIES_LOADED,
    payload: [{ id: 1 }],
  });
  state = rootReducer(state, { type: CLEAR_FINANCE });

  assert.deepEqual(state.companies.items, []);
  assert.equal(state.companies.status, 'idle');
  assert.deepEqual(state.invoices.sales, []);
  assert.deepEqual(state.invoices.purchases, []);
  assert.equal(state.dashboard.summary, null);
  assert.equal(state.session.generation, 1);
});
