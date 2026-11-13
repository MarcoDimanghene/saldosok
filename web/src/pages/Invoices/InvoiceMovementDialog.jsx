import { useEffect, useRef, useState } from 'react';
import { Button } from '../../component/ui/UIComponents';
import { createCollection, createPayment } from '../../services/paymentService';
import {
  DialogActions,
  Form,
  FormField,
  FormGrid,
  FormInput,
  InvoiceDetailGrid,
  InvoiceDetailItem,
  InvoiceDialogContent,
  MovementDialog,
  SectionHeading,
  StatusMessage,
} from './Invoices.styles';

const today = new Date().toISOString().slice(0, 10);
const currency = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 2,
});

const InvoiceMovementDialog = ({ direction, invoice, onClose, onCreated }) => {
  const dialogRef = useRef(null);
  const [form, setForm] = useState({
    amount: '',
    date: today,
    method: 'Transferencia',
    receiptNumber: '',
    notes: '',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const isCollection = direction === 'sales';
  const movementLabel = isCollection ? 'cobro' : 'pago';
  const fieldPrefix = `invoice-${direction}-${invoice.id}-${movementLabel}`;
  const paidAmount = Number(
    isCollection ? invoice.monto_cobrado : invoice.monto_pagado,
  ) || 0;
  const outstandingAmount = Math.max(
    Number(
      invoice.saldo_pendiente
      ?? Number(invoice.monto_ajustado ?? invoice.monto_total ?? 0) - paidAmount,
    ),
    0,
  );
  const invoiceLabel = invoice.numero_interno
    || `${invoice.letra || '—'} ${invoice.punto_venta ?? '—'}-${invoice.nro_factura ?? '—'}`;

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return undefined;
    const handleClose = () => onClose();
    dialog.addEventListener('close', handleClose);
    if (!dialog.open) dialog.showModal();

    return () => {
      dialog.removeEventListener('close', handleClose);
      if (dialog.open) dialog.close();
    };
  }, [onClose]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    if (Number(form.amount) > outstandingAmount) {
      setError(
        `El importe supera el saldo pendiente (${currency.format(outstandingAmount)}).`,
      );
      return;
    }
    setIsSaving(true);
    const commonData = {
      invoice_id: invoice.id,
      amount: form.amount,
      receipt_number: form.receiptNumber.trim() || null,
      notes: form.notes.trim() || null,
    };

    try {
      if (isCollection) {
        await createCollection({
          ...commonData,
          collection_date: form.date,
          collection_method: form.method.trim() || null,
        });
      } else {
        await createPayment({
          ...commonData,
          payment_date: form.date,
          payment_method: form.method.trim() || null,
        });
      }
      await onCreated(direction);
    } catch (saveError) {
      setError(saveError.message || `No se pudo registrar el ${movementLabel}.`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <MovementDialog
      ref={dialogRef}
      closedby="closerequest"
      aria-labelledby="invoice-movement-title"
    >
      <InvoiceDialogContent>
        <SectionHeading>
          <div>
            <h2 id="invoice-movement-title">Registrar {movementLabel}</h2>
            <span>Completá los datos del movimiento.</span>
          </div>
        </SectionHeading>

        <InvoiceDetailGrid>
          <InvoiceDetailItem>
            <span>Factura</span>
            <strong>{invoiceLabel}</strong>
          </InvoiceDetailItem>
          <InvoiceDetailItem>
            <span>Saldo pendiente</span>
            <strong>{currency.format(outstandingAmount)}</strong>
          </InvoiceDetailItem>
        </InvoiceDetailGrid>

        {error && <StatusMessage $error role="alert">{error}</StatusMessage>}
        <Form onSubmit={handleSubmit}>
          <FormGrid>
            <FormField>
              <label htmlFor={`${fieldPrefix}-amount`}>Importe</label>
              <FormInput
                autoFocus
                id={`${fieldPrefix}-amount`}
                type="number"
                min="0.01"
                max={outstandingAmount.toFixed(2)}
                step="0.01"
                value={form.amount}
                onChange={(event) => setForm({ ...form, amount: event.target.value })}
                required
              />
            </FormField>
            <FormField>
              <label htmlFor={`${fieldPrefix}-date`}>
                Fecha del {movementLabel}
              </label>
              <FormInput
                id={`${fieldPrefix}-date`}
                type="date"
                value={form.date}
                onChange={(event) => setForm({ ...form, date: event.target.value })}
                required
              />
            </FormField>
            <FormField>
              <label htmlFor={`${fieldPrefix}-method`}>Medio</label>
              <FormInput
                id={`${fieldPrefix}-method`}
                value={form.method}
                onChange={(event) => setForm({ ...form, method: event.target.value })}
                placeholder="Transferencia, efectivo, cheque…"
              />
            </FormField>
            <FormField>
              <label htmlFor={`${fieldPrefix}-receipt`}>Comprobante (opcional)</label>
              <FormInput
                id={`${fieldPrefix}-receipt`}
                value={form.receiptNumber}
                onChange={(event) => setForm({
                  ...form,
                  receiptNumber: event.target.value,
                })}
              />
            </FormField>
            <FormField $fullWidth>
              <label htmlFor={`${fieldPrefix}-notes`}>Notas (opcional)</label>
              <FormInput
                as="textarea"
                id={`${fieldPrefix}-notes`}
                value={form.notes}
                onChange={(event) => setForm({ ...form, notes: event.target.value })}
              />
            </FormField>
          </FormGrid>
          <DialogActions>
            <Button
              type="button"
              $variant="secondary"
              onClick={() => dialogRef.current?.close()}
              disabled={isSaving}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? 'Guardando…' : `Guardar ${movementLabel}`}
            </Button>
          </DialogActions>
        </Form>
      </InvoiceDialogContent>
    </MovementDialog>
  );
};

export default InvoiceMovementDialog;
