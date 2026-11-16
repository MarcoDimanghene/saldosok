import assert from 'node:assert/strict';
import test from 'node:test';
import {
  filterOperatingResults,
  initialOperatingResultFilters,
} from '../src/pages/OperatingResults/operatingResultsFilters.js';

const results = [
  {
    factura_compra_id: 1,
    fecha_emision: '2026-10-12',
    proveedor: 'Compañía Norte',
    letra: 'A',
    punto_venta: 4,
    nro_factura: 125,
    numero_interno: 'COMP-1',
  },
  {
    factura_compra_id: 2,
    fecha_emision: '2026-10-20',
    proveedor: 'Servicios Sur',
    letra: 'B',
    punto_venta: 2,
    nro_factura: 9,
    numero_interno: 'COMP-2',
  },
];

test('filters operating results by an inclusive date range and company text', () => {
  const filtered = filterOperatingResults(results, {
    ...initialOperatingResultFilters,
    dateFrom: '2026-10-12',
    dateTo: '2026-10-19',
    company: 'COMPAÑÍA',
  });

  assert.deepEqual(filtered.map((invoice) => invoice.factura_compra_id), [1]);
});

test('searches invoice numbers as the user types, ignoring letter case', () => {
  const filtered = filterOperatingResults(results, {
    ...initialOperatingResultFilters,
    invoice: 'a 4-125',
  });

  assert.deepEqual(filtered.map((invoice) => invoice.factura_compra_id), [1]);
});
