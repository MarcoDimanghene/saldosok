import assert from 'node:assert/strict';
import test from 'node:test';
import { filterInvoices } from '../src/pages/Invoices/invoiceFilters.js';

const noFilters = {
  status: 'all',
  dateFrom: '',
  dateTo: '',
  company: 'all',
};

const sales = [
  {
    id: 1,
    estado: 'pendiente',
    fecha_emision: '2026-10-10',
    emisor_id: 4,
    cliente_id: 8,
  },
  {
    id: 2,
    estado: 'pagado',
    fecha_emision: '2026-11-02',
    emisor_id: 4,
    cliente_id: 9,
  },
];

test('filters sales invoices by state, inclusive date range, and either company role', () => {
  const results = filterInvoices(sales, {
    ...noFilters,
    status: 'pendiente',
    dateFrom: '2026-10-10',
    dateTo: '2026-10-10',
    company: '8',
  }, 'sales');

  assert.deepEqual(results.map(({ id }) => id), [1]);
});

test('filters purchases by supplier or recipient and uses creation date when issue date is absent', () => {
  const purchases = [
    {
      id: 1,
      estado: 'pendiente',
      fecha_creacion: '2026-10-15T12:00:00',
      proveedor_id: 8,
      receptor_id: 11,
    },
    { id: 2, estado: 'pagado', fecha_emision: '2026-10-15', proveedor_id: 9, receptor_id: 12 },
  ];

  const results = filterInvoices(purchases, {
    ...noFilters,
    dateFrom: '2026-10-15',
    dateTo: '2026-10-15',
    company: '8',
  }, 'purchases');

  assert.deepEqual(results.map(({ id }) => id), [1]);

  const recipientResults = filterInvoices(purchases, {
    ...noFilters,
    company: '12',
  }, 'purchases');

  assert.deepEqual(recipientResults.map(({ id }) => id), [2]);
});
