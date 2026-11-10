const SHEETS = {
  Empresas: [
    { key: 'cuit', header: 'CUIT/CUIL', width: 18, text: true },
    { key: 'razon_social', header: 'Razón social', width: 32, text: true },
    { key: 'condicion_iva', header: 'Condición de IVA', width: 24, text: true },
    { key: 'domicilio', header: 'Domicilio', width: 32, text: true },
    { key: 'localidad', header: 'Localidad', width: 24, text: true },
    { key: 'provincia', header: 'Provincia', width: 24, text: true },
    { key: 'es_cliente', header: 'Es cliente (Sí/No)', width: 20, text: true },
    { key: 'es_proveedor', header: 'Es proveedor (Sí/No)', width: 22, text: true },
    { key: 'es_emisor', header: 'Es emisor (Sí/No)', width: 20, text: true },
  ],
  Ventas: [
    { key: 'cuit_emisor', header: 'CUIT emisor', width: 18, text: true },
    { key: 'cuit_cliente', header: 'CUIT cliente', width: 18, text: true },
    { key: 'letra', header: 'Letra', width: 10, text: true },
    { key: 'punto_venta', header: 'Punto de venta', width: 16 },
    { key: 'numero_factura', header: 'Nro factura', width: 16 },
    { key: 'fecha_emision', header: 'Fecha de emisión', width: 18, date: true },
    { key: 'fecha_vencimiento', header: 'Fecha estimada de cobro', width: 24, date: true },
    { key: 'cae', header: 'CAE', width: 24, text: true },
    { key: 'importe', header: 'Importe', width: 16, amount: true },
  ],
  Compras: [
    { key: 'cuit_proveedor', header: 'CUIT proveedor', width: 18, text: true },
    { key: 'letra', header: 'Letra', width: 10, text: true },
    { key: 'punto_venta', header: 'Punto de venta', width: 16 },
    { key: 'numero_factura', header: 'Nro factura', width: 16 },
    { key: 'fecha_emision', header: 'Fecha de emisión', width: 18, date: true },
    { key: 'fecha_vencimiento', header: 'Fecha de vencimiento', width: 22, date: true },
    { key: 'cae', header: 'CAE', width: 24, text: true },
    { key: 'concepto', header: 'Concepto', width: 32, text: true },
    { key: 'importe', header: 'Importe', width: 16, amount: true },
    { key: 'moneda', header: 'Moneda', width: 12, text: true },
  ],
  Cobros: [
    { key: 'cuit_emisor', header: 'CUIT emisor', width: 18, text: true },
    { key: 'cuit_cliente', header: 'CUIT cliente', width: 18, text: true },
    { key: 'letra', header: 'Letra', width: 10, text: true },
    { key: 'punto_venta', header: 'Punto de venta', width: 16 },
    { key: 'numero_factura', header: 'Nro factura', width: 16 },
    { key: 'fecha', header: 'Fecha de cobro', width: 18, date: true },
    { key: 'importe', header: 'Importe', width: 16, amount: true },
    { key: 'medio', header: 'Medio de cobro', width: 20, text: true },
    { key: 'comprobante', header: 'Nro comprobante', width: 22, text: true },
    { key: 'notas', header: 'Notas', width: 32, text: true },
  ],
  Pagos: [
    { key: 'cuit_proveedor', header: 'CUIT proveedor', width: 18, text: true },
    { key: 'letra', header: 'Letra', width: 10, text: true },
    { key: 'punto_venta', header: 'Punto de venta', width: 16 },
    { key: 'numero_factura', header: 'Nro factura', width: 16 },
    { key: 'fecha', header: 'Fecha de pago', width: 18, date: true },
    { key: 'importe', header: 'Importe', width: 16, amount: true },
    { key: 'medio', header: 'Medio de pago', width: 20, text: true },
    { key: 'comprobante', header: 'Nro comprobante', width: 22, text: true },
    { key: 'notas', header: 'Notas', width: 32, text: true },
  ],
};

const toIsoDate = (value) => {
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    const year = value.getUTCFullYear();
    const month = String(value.getUTCMonth() + 1).padStart(2, '0');
    const day = String(value.getUTCDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  if (typeof value === 'number' && Number.isFinite(value)) {
    const date = new Date(Date.UTC(1899, 11, 30) + value * 86400000);
    return date.toISOString().slice(0, 10);
  }
  const text = String(value || '').trim();
  const dayFirstDate = text.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (dayFirstDate) {
    return `${dayFirstDate[3]}-${dayFirstDate[2].padStart(2, '0')}-${dayFirstDate[1].padStart(2, '0')}`;
  }
  return text;
};

const getCellValue = (cell, column) => {
  const value = cell.value;
  if (value == null || value === '') return '';
  if (value && typeof value === 'object' && !(value instanceof Date)) {
    throw new Error(`La celda ${cell.address} no puede contener fórmulas.`);
  }
  if (column.date) return toIsoDate(value);
  if (typeof value === 'string') return value.trim();
  return value;
};

const loadExcelJS = async () => {
  const { default: ExcelJS } = await import('exceljs');
  return ExcelJS;
};

export const downloadFinanceTemplate = async () => {
  const ExcelJS = await loadExcelJS();
  const workbook = new ExcelJS.Workbook();
  const instructions = workbook.addWorksheet('Instrucciones');
  instructions.columns = [{ width: 112 }];
  instructions.addRows([
    ['Plantilla de migración financiera - Saldo Ok'],
    ['Completá las hojas Empresas, Ventas, Compras, Cobros y Pagos según los encabezados. Podés dejar vacías las hojas que no necesites.'],
    ['En Empresas, indicá al menos un rol por fila: cliente, proveedor, emisor o una combinación. Podés omitir el CUIT/CUIL únicamente para proveedores que no sean clientes ni emisores.'],
    ['La hoja Empresas crea registros nuevos; si el CUIT/CUIL ya existe, se informa un error y no se modifica ningún dato existente.'],
    ['La fila marcada como emisor actualiza el perfil fiscal de tu organización y sincroniza su emisor. Solo puede haber un emisor por archivo.'],
    ['Las compras que se importan deben tener factura formal. Cobros y pagos se vinculan por CUIT y número de factura.'],
    ['Las facturas deben estar en la hoja correspondiente o ya existir en Saldo Ok. Las empresas incluidas en esta planilla pueden usarse en las facturas del mismo archivo.'],
    ['Usá fechas de Excel o el formato AAAA-MM-DD. Los importes deben ser positivos, con hasta dos decimales. No incluyas fórmulas.'],
    ['La importación es integral: si hay una fila inválida o una factura duplicada, no se guarda ningún dato. Corregí los errores y volvé a importar.'],
    ['No cambies los nombres de las hojas ni los encabezados. El límite es de 5.000 filas de datos por archivo.'],
  ]);
  instructions.getRow(1).font = { bold: true, size: 16, color: { argb: 'FF103A4A' } };
  instructions.getColumn(1).alignment = { wrapText: true, vertical: 'middle' };
  instructions.eachRow((row, rowNumber) => {
    row.height = rowNumber === 1 ? 30 : 36;
  });

  Object.entries(SHEETS).forEach(([name, columns]) => {
    const worksheet = workbook.addWorksheet(name);
    worksheet.columns = columns.map((column) => ({
      header: column.header,
      key: column.key,
      width: column.width,
      style: column.text
        ? { numFmt: '@' }
        : column.date
          ? { numFmt: 'dd/mm/yyyy' }
          : column.amount
            ? { numFmt: '#,##0.00' }
            : undefined,
    }));
    worksheet.views = [{ state: 'frozen', ySplit: 1 }];
    worksheet.autoFilter = {
      from: 'A1',
      to: `${worksheet.getColumn(columns.length).letter}1`,
    };
    const header = worksheet.getRow(1);
    header.height = 28;
    header.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    header.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF123047' },
    };
    header.alignment = { vertical: 'middle', wrapText: true };
  });

  const buffer = await workbook.xlsx.writeBuffer();
  const url = URL.createObjectURL(
    new Blob([buffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }),
  );
  const link = document.createElement('a');
  link.href = url;
  link.download = 'plantilla_importacion_saldo_ok.xlsx';
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
};

export const readFinanceWorkbook = async (file) => {
  const ExcelJS = await loadExcelJS();
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.load(await file.arrayBuffer());
  const records = {};

  Object.entries(SHEETS).forEach(([name, columns]) => {
    const worksheet = workbook.getWorksheet(name);
    if (!worksheet) {
      throw new Error(`Falta la hoja «${name}». Usá la plantilla oficial.`);
    }

    const headersMatch = columns.every(
      (column, index) => String(worksheet.getRow(1).getCell(index + 1).value || '').trim() === column.header,
    );
    if (!headersMatch) {
      throw new Error(`Los encabezados de la hoja «${name}» fueron modificados. Usá la plantilla oficial.`);
    }

    records[name] = [];
    worksheet.eachRow((row, rowNumber) => {
      if (rowNumber === 1) return;
      const values = columns.map((column, index) => getCellValue(row.getCell(index + 1), column));
      if (values.every((value) => value === '')) return;
      records[name].push({
        rowNumber,
        ...Object.fromEntries(columns.map((column, index) => [column.key, values[index]])),
      });
    });
  });

  return {
    companies: records.Empresas,
    sales: records.Ventas,
    purchases: records.Compras,
    collections: records.Cobros,
    payments: records.Pagos,
  };
};
