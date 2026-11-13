const NOTE_TYPES = new Set(['nota_credito', 'nota_debito']);

export function applyInvoiceBalances(invoices, direction) {
  const childrenByOrigin = new Map();
  const invoiceData = new Map();

  invoices.forEach((invoice) => {
    invoiceData.set(invoice.id, invoice);
    if (invoice.factura_origen_id != null) {
      const children = childrenByOrigin.get(invoice.factura_origen_id) || [];
      children.push(invoice.id);
      childrenByOrigin.set(invoice.factura_origen_id, children);
    }
  });

  const adjustmentFor = (invoiceId, ancestors = new Set()) => {
    if (ancestors.has(invoiceId)) return 0;
    const descendants = new Set(ancestors).add(invoiceId);
    return (childrenByOrigin.get(invoiceId) || []).reduce((total, childId) => {
      const child = invoiceData.get(childId);
      if (!child || !NOTE_TYPES.has(child.tipo_comprobante)) return total;
      const amount = Number(child.monto_total) || 0;
      const signedAmount = child.tipo_comprobante === 'nota_credito' ? -amount : amount;
      return total + signedAmount + adjustmentFor(childId, descendants);
    }, 0);
  };

  return invoices.map((invoice) => {
    if (NOTE_TYPES.has(invoice.tipo_comprobante)) return invoice;

    const adjustedTotal = invoice.monto_ajustado != null
      ? Number(invoice.monto_ajustado)
      : (Number(invoice.monto_total) || 0) + adjustmentFor(invoice.id);
    const paidTotal = Number(
      direction === 'sales' ? invoice.monto_cobrado : invoice.monto_pagado,
    ) || 0;

    return {
      ...invoice,
      monto_ajustado: adjustedTotal,
      saldo_pendiente: invoice.saldo_pendiente != null
        ? Number(invoice.saldo_pendiente)
        : Math.max(adjustedTotal - paidTotal, 0),
    };
  });
}
