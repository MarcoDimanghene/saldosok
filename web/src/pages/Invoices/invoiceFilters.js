export function filterInvoices(invoices, filters, type) {
  return invoices.filter((invoice) => {
    if (filters.status !== 'all' && invoice.estado !== filters.status) return false;

    const rawDate = invoice.fecha_emision || invoice.fecha_creacion || '';
    const invoiceDate = String(rawDate).slice(0, 10);
    if (filters.dateFrom && (!invoiceDate || invoiceDate < filters.dateFrom)) return false;
    if (filters.dateTo && (!invoiceDate || invoiceDate > filters.dateTo)) return false;

    if (filters.company !== 'all') {
      const companyId = type === 'sales'
        ? [invoice.emisor_id, invoice.cliente_id]
        : [invoice.proveedor_id, invoice.receptor_id];
      if (!companyId.some((id) => String(id) === filters.company)) return false;
    }

    return true;
  });
}
