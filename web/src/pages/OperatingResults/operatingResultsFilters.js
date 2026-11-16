export const initialOperatingResultFilters = {
  dateFrom: '',
  dateTo: '',
  company: '',
  invoice: '',
};

const invoiceLabel = (invoice) => (
  invoice.letra && invoice.punto_venta != null && invoice.nro_factura != null
    ? `${invoice.letra} ${invoice.punto_venta}-${invoice.nro_factura}`
    : invoice.numero_interno || `#${invoice.factura_compra_id}`
);

export function filterOperatingResults(results, filters) {
  const companyTerm = filters.company.trim().toLocaleLowerCase();
  const invoiceTerm = filters.invoice.trim().toLocaleLowerCase();

  return results.filter((invoice) => {
    const invoiceDate = String(invoice.fecha_emision || '').slice(0, 10);
    if (filters.dateFrom && (!invoiceDate || invoiceDate < filters.dateFrom)) return false;
    if (filters.dateTo && (!invoiceDate || invoiceDate > filters.dateTo)) return false;

    if (companyTerm && !String(invoice.proveedor || '').toLocaleLowerCase().includes(companyTerm)) {
      return false;
    }

    const searchableInvoice = [
      invoiceLabel(invoice),
      invoice.numero_interno,
      invoice.factura_compra_id,
    ].filter((value) => value != null).join(' ').toLocaleLowerCase();
    if (invoiceTerm && !searchableInvoice.includes(invoiceTerm)) return false;

    return true;
  });
}
