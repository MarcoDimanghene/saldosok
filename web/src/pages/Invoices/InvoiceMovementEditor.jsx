import { useEffect, useState } from 'react';
import { Button } from '../../component/ui/UIComponents';
import {
  getCollectionsByInvoiceId,
  getPaymentsByInvoiceId,
  updateCollection,
  updatePayment,
} from '../../services/paymentService';
import {
  EmptyState,
  Form,
  FormField,
  FormGrid,
  FormInput,
  MovementCard,
  MovementList,
  StatusMessage,
} from './Invoices.styles';

const today = new Date().toISOString().slice(0, 10);

const MovementForm = ({ movement, direction, onSave }) => {
  const isCollection = direction === 'sales';
  const [form, setForm] = useState({
    amount: String(movement.monto ?? ''),
    date: (isCollection ? movement.fecha_cobro : movement.fecha_pago) || today,
    method: (isCollection ? movement.metodo_cobro : movement.metodo_pago) || '',
    receiptNumber: movement.nro_comprobante || '',
    notes: movement.notas || '',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const movementLabel = isCollection ? 'cobro' : 'pago';
  const prefix = `${movementLabel}-${movement.id}`;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setIsSaving(true);
    const data = {
      invoice_id: isCollection ? movement.factura_venta_id : movement.factura_compra_id,
      amount: form.amount,
      ...(isCollection
        ? { collection_date: form.date, collection_method: form.method || null }
        : { payment_date: form.date, payment_method: form.method || null }),
      receipt_number: form.receiptNumber.trim() || null,
      notes: form.notes.trim() || null,
    };

    try {
      await onSave(movement.id, data);
    } catch (saveError) {
      setError(saveError.message || `No se pudo actualizar el ${movementLabel}.`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <MovementCard>
      <h3>{isCollection ? 'Cobro' : 'Pago'} · {form.date}</h3>
      {error && <StatusMessage $error role="alert">{error}</StatusMessage>}
      <Form onSubmit={handleSubmit}>
        <FormGrid>
          <FormField>
            <label htmlFor={`${prefix}-amount`}>Importe</label>
            <FormInput
              id={`${prefix}-amount`}
              type="number"
              min="0.01"
              step="0.01"
              value={form.amount}
              onChange={(event) => setForm({ ...form, amount: event.target.value })}
              required
            />
          </FormField>
          <FormField>
            <label htmlFor={`${prefix}-date`}>Fecha</label>
            <FormInput
              id={`${prefix}-date`}
              type="date"
              value={form.date}
              onChange={(event) => setForm({ ...form, date: event.target.value })}
              required
            />
          </FormField>
          <FormField>
            <label htmlFor={`${prefix}-method`}>Medio</label>
            <FormInput
              id={`${prefix}-method`}
              value={form.method}
              onChange={(event) => setForm({ ...form, method: event.target.value })}
            />
          </FormField>
          <FormField>
            <label htmlFor={`${prefix}-receipt`}>Comprobante</label>
            <FormInput
              id={`${prefix}-receipt`}
              value={form.receiptNumber}
              onChange={(event) => setForm({ ...form, receiptNumber: event.target.value })}
            />
          </FormField>
          <FormField>
            <label htmlFor={`${prefix}-notes`}>Notas</label>
            <FormInput
              as="textarea"
              id={`${prefix}-notes`}
              value={form.notes}
              onChange={(event) => setForm({ ...form, notes: event.target.value })}
            />
          </FormField>
        </FormGrid>
        <Button type="submit" disabled={isSaving}>
          {isSaving ? 'Guardando…' : `Guardar cambios del ${movementLabel}`}
        </Button>
      </Form>
    </MovementCard>
  );
};

const InvoiceMovementEditor = ({ direction, invoiceId, onUpdated }) => {
  const [movements, setMovements] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isCurrent = true;
    const loadMovements = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const result = direction === 'sales'
          ? await getCollectionsByInvoiceId(invoiceId)
          : await getPaymentsByInvoiceId(invoiceId);
        if (isCurrent) setMovements(result);
      } catch (loadError) {
        if (isCurrent) {
          setError(loadError.message || 'No se pudieron cargar los movimientos.');
        }
      } finally {
        if (isCurrent) setIsLoading(false);
      }
    };
    loadMovements();

    return () => {
      isCurrent = false;
    };
  }, [direction, invoiceId]);

  const handleSave = async (movementId, data) => {
    const updatedMovement = direction === 'sales'
      ? await updateCollection(movementId, data)
      : await updatePayment(movementId, data);
    setMovements((current) => current.map((movement) => (
      movement.id === movementId ? updatedMovement : movement
    )));
    await onUpdated();
  };

  if (isLoading) return <p role="status">Cargando movimientos…</p>;
  if (error) return <StatusMessage $error role="alert">{error}</StatusMessage>;
  if (!movements.length) {
    return <EmptyState>Esta factura todavía no tiene movimientos registrados.</EmptyState>;
  }

  return (
    <MovementList>
      {movements.map((movement) => (
        <MovementForm
          key={movement.id}
          movement={movement}
          direction={direction}
          onSave={handleSave}
        />
      ))}
    </MovementList>
  );
};

export default InvoiceMovementEditor;
