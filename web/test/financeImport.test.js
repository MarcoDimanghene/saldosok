import assert from 'node:assert/strict';
import test from 'node:test';
import ExcelJS from 'exceljs';
import { readFinanceWorkbook } from '../src/pages/ImportExcel/excelTemplate.js';

const sheetHeaders = {
  Empresas: [
    'CUIT/CUIL',
    'Razón social',
    'Condición de IVA',
    'Domicilio',
    'Localidad',
    'Provincia',
    'Es cliente (Sí/No)',
    'Es proveedor (Sí/No)',
    'Es emisor (Sí/No)',
  ],
  Ventas: [
    'CUIT emisor',
    'CUIT cliente',
    'Letra',
    'Punto de venta',
    'Nro factura',
    'Fecha de emisión',
    'Fecha estimada de cobro',
    'CAE',
    'Importe',
  ],
  Compras: [
    'CUIT proveedor',
    'Letra',
    'Punto de venta',
    'Nro factura',
    'Fecha de emisión',
    'Fecha de vencimiento',
    'CAE',
    'Concepto',
    'Importe',
    'Moneda',
  ],
  Cobros: [
    'CUIT emisor',
    'CUIT cliente',
    'Letra',
    'Punto de venta',
    'Nro factura',
    'Fecha de cobro',
    'Importe',
    'Medio de cobro',
    'Nro comprobante',
    'Notas',
  ],
  Pagos: [
    'CUIT proveedor',
    'Letra',
    'Punto de venta',
    'Nro factura',
    'Fecha de pago',
    'Importe',
    'Medio de pago',
    'Nro comprobante',
    'Notas',
  ],
};

const asFile = async (workbook) => {
  const buffer = await workbook.xlsx.writeBuffer();
  return {
    arrayBuffer: async () => buffer.buffer.slice(
      buffer.byteOffset,
      buffer.byteOffset + buffer.byteLength,
    ),
  };
};

const excelDateSerial = (year, month, day) => (
  (Date.UTC(year, month - 1, day) - Date.UTC(1899, 11, 30)) / 86400000
);

test('reads rows from all finance sheets and normalizes Excel dates', async () => {
  const workbook = new ExcelJS.Workbook();
  Object.entries(sheetHeaders).forEach(([name, headers]) => {
    const sheet = workbook.addWorksheet(name);
    sheet.addRow(headers);
    sheet.addRow(Array(headers.length).fill(''));
  });
  const sales = workbook.getWorksheet('Ventas');
  workbook.getWorksheet('Empresas').addRow([
    '20333333333',
    'Proveedor de prueba',
    '',
    '',
    '',
    '',
    'No',
    'Sí',
    'No',
  ]);
  sales.addRow([
    '20111111111',
    '20222222222',
    'A',
    1,
    42,
    excelDateSerial(2026, 10, 1),
    excelDateSerial(2026, 11, 1),
    '',
    100.5,
  ]);
  sales.getCell('F3').numFmt = 'dd/mm/yyyy';
  sales.getCell('G3').numFmt = 'dd/mm/yyyy';

  const result = await readFinanceWorkbook(await asFile(workbook));
  assert.equal(result.sales.length, 1);
  assert.equal(result.sales[0].rowNumber, 3);
  assert.equal(result.sales[0].fecha_emision, '2026-10-01');
  assert.equal(result.sales[0].importe, 100.5);
  assert.equal(result.companies.length, 1);
  assert.equal(result.companies[0].cuit, '20333333333');
  assert.equal(result.companies[0].es_proveedor, 'Sí');
  assert.deepEqual(result.purchases, []);
  assert.deepEqual(result.collections, []);
  assert.deepEqual(result.payments, []);
});

test('rejects formula cells in an import workbook', async () => {
  const workbook = new ExcelJS.Workbook();
  Object.entries(sheetHeaders).forEach(([name, headers]) => {
    workbook.addWorksheet(name).addRow(headers);
  });
  const sales = workbook.getWorksheet('Ventas');
  sales.addRow([
    '20111111111',
    '20222222222',
    'A',
    1,
    42,
    '2026-10-01',
    '2026-11-01',
    '',
    { formula: '50+50', result: 100 },
  ]);

  await assert.rejects(
    readFinanceWorkbook(await asFile(workbook)),
    /celda I2 no puede contener fórmulas/,
  );
});
