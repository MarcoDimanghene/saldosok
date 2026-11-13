import assert from 'node:assert/strict';
import test from 'node:test';
import { applyInvoiceBalances } from '../src/pages/Invoices/invoiceBalances.js';

test('subtracts linked credit notes from the invoice balance after collections', () => {
  const invoices = applyInvoiceBalances([
    {
      id: 1,
      monto_total: '100.00',
      monto_cobrado: '20.00',
      tipo_comprobante: 'factura',
    },
    {
      id: 2,
      monto_total: '30.00',
      tipo_comprobante: 'nota_credito',
      factura_origen_id: 1,
    },
    {
      id: 3,
      monto_total: '10.00',
      tipo_comprobante: 'nota_debito',
      factura_origen_id: 1,
    },
  ], 'sales');

  assert.equal(invoices[0].monto_ajustado, 80);
  assert.equal(invoices[0].saldo_pendiente, 60);
});

test('a debit note linked to a credit note restores the deducted amount', () => {
  const invoices = applyInvoiceBalances([
    { id: 1, monto_total: '100.00', tipo_comprobante: 'factura' },
    {
      id: 2,
      monto_total: '40.00',
      tipo_comprobante: 'nota_credito',
      factura_origen_id: 1,
    },
    {
      id: 3,
      monto_total: '40.00',
      tipo_comprobante: 'nota_debito',
      factura_origen_id: 2,
    },
  ], 'sales');

  assert.equal(invoices[0].monto_ajustado, 100);
  assert.equal(invoices[0].saldo_pendiente, 100);
});

test('uses server-calculated balances when available', () => {
  const [invoice] = applyInvoiceBalances([{
    id: 1,
    monto_total: '100.00',
    monto_ajustado: '75.00',
    saldo_pendiente: '35.00',
    monto_pagado: '40.00',
    tipo_comprobante: 'factura',
  }], 'purchases');

  assert.equal(invoice.monto_ajustado, 75);
  assert.equal(invoice.saldo_pendiente, 35);
});
