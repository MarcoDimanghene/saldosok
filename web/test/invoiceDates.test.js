import assert from 'node:assert/strict';
import test from 'node:test';
import {
  addDaysToDate,
  daysUntil,
  formatDateCountdown,
  formatInvoiceDate,
} from '../src/pages/Invoices/invoiceDates.js';

test('adds company payment terms to invoice dates without timezone shifts', () => {
  assert.equal(addDaysToDate('2026-11-12', 30), '2026-12-12');
  assert.equal(addDaysToDate('2026-12-20', '15'), '2027-01-04');
  assert.equal(addDaysToDate('2024-02-28', 1), '2024-02-29');
  assert.equal(addDaysToDate('2026-11-12', ''), '');
  assert.equal(addDaysToDate('invalid', 10), '');
});

test('counts days to due dates without timezone shifts', () => {
  assert.equal(daysUntil('2026-11-15', '2026-11-11'), 4);
  assert.equal(daysUntil('2026-11-10', '2026-11-11'), -1);
  assert.equal(daysUntil('2026-11-11', '2026-11-11'), 0);
});

test('formats due and estimated collection countdowns', () => {
  assert.equal(formatDateCountdown('2026-11-15', 'due', '2026-11-11'), 'Vence en 4 días');
  assert.equal(formatDateCountdown('2026-11-10', 'due', '2026-11-11'), 'Vencida hace 1 día');
  assert.equal(formatDateCountdown('2026-11-11', 'collection', '2026-11-11'), 'Cobro estimado hoy');
  assert.equal(formatDateCountdown('invalid', 'due', '2026-11-11'), null);
});

test('formats invoice dates for display', () => {
  assert.equal(formatInvoiceDate('2026-11-15'), '15/11/2026');
  assert.equal(formatInvoiceDate(null), null);
});
