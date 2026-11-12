import { useMemo, useState } from 'react';
import { TbPlus } from 'react-icons/tb';
import { Button } from '../../component/ui/UIComponents';
import { INVOICE_LETTERS, INVOICE_TYPE_LABELS } from '../../config/appConfig';
import {
  createPurchaseInvoice,
  createSalesInvoice,
} from '../../services/invoiceService';
import {
  EmptyState,
  Form,
  FormField,
  FormGrid,
  FormInput,
  StatusMessage,
} from './Invoices.styles';

const today = new Date().toISOString().slice(0, 10);
const initialForm = {
  direction: 'sales',
  type: 'nota_credito',
  originId: '',
  letter: 'A',
  pointOfSale: '',
  invoiceNumber: '',
  issueDate: today,
  estimatedPaymentDate: today,
  dueDate: '',
  cae: '',
  totalAmount: '',
};
const currency = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 2,
});
const formatInvoiceNumber = (invoice) => (
  `${invoice.letra || '—'} ${invoice.punto_venta ?? '—'}-${invoice.nro_factura ?? '—'}`
);

const InvoiceNotes = ({
  companies,
  salesInvoices,
  purchaseInvoices,
  isLoading,
  onCreated,
}) => {
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState(null);
  const companyNames = useMemo(
    () => new Map(companies.map((company) => [company.id, company.razon_social])),
    [companies],
  );
  const originInvoices = useMemo(() => {
    const invoices = form.direction === 'sales' ? salesInvoices : purchaseInvoices;
    return invoices.filter((invoice) => (
      (!invoice.tipo_comprobante || invoice.tipo_comprobante === 'factura')
      && (form.direction === 'sales'
        ? Boolean(invoice.emisor_id && invoice.cliente_id)
        : invoice.factura_recibida)
    ));
  }, [form.direction, purchaseInvoices, salesInvoices]);
  const selectedOrigin = originInvoices.find(
    (invoice) => invoice.id === Number(form.originId),
  );

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage(null);
    if (!selectedOrigin) {
      setMessage({ error: true, text: 'Selecciona la factura de origen de la nota.' });
      return;
    }
    setIsSubmitting(true);

    try {
      const invoiceData = {
        letter: form.letter,
        point_of_sale: Number(form.pointOfSale),
        invoice_number: Number(form.invoiceNumber),
        issue_date: form.issueDate,
        cae: form.cae.trim() || null,
        total_amount: form.totalAmount,
        tipo_comprobante: form.type,
        factura_origen_id: selectedOrigin.id,
      };

      if (form.direction === 'sales') {
        await createSalesInvoice({
          ...invoiceData,
          issuer_id: selectedOrigin.emisor_id,
          receiver_id: selectedOrigin.cliente_id,
          estimated_payment_date: form.estimatedPaymentDate,
        });
      } else {
        await createPurchaseInvoice({
          ...invoiceData,
          issuer_id: selectedOrigin.proveedor_id,
          due_date: form.dueDate || null,
        });
      }

      await onCreated(form.direction);
      setForm({ ...initialForm, direction: form.direction });
      setMessage({
        error: false,
        text: `${INVOICE_TYPE_LABELS[form.type]} registrada y vinculada correctamente.`,
      });
    } catch (error) {
      setMessage({
        error: true,
        text: error.message || 'No se pudo registrar la nota.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDirectionChange = (direction) => {
    setForm({ ...form, direction, originId: '' });
  };

  return (
    <Form onSubmit={handleSubmit}>
      {message && (
        <StatusMessage $error={message.error} role={message.error ? 'alert' : 'status'}>
          {message.text}
        </StatusMessage>
      )}
      <FormGrid>
        <FormField>
          <label htmlFor="note-direction">Operación relacionada</label>
          <FormInput
            as="select"
            id="note-direction"
            value={form.direction}
            onChange={(event) => handleDirectionChange(event.target.value)}
            required
          >
            <option value="sales">Venta</option>
            <option value="purchases">Compra</option>
          </FormInput>
        </FormField>
        <FormField>
          <label htmlFor="note-type">Tipo de nota</label>
          <FormInput
            as="select"
            id="note-type"
            value={form.type}
            onChange={(event) => setForm({ ...form, type: event.target.value })}
            required
          >
            <option value="nota_credito">Nota de crédito</option>
            <option value="nota_debito">Nota de débito</option>
          </FormInput>
        </FormField>
        <FormField>
          <label htmlFor="note-origin">Factura de origen</label>
          <FormInput
            as="select"
            id="note-origin"
            value={form.originId}
            onChange={(event) => setForm({ ...form, originId: event.target.value })}
            disabled={isLoading || !originInvoices.length}
            required
          >
            <option value="">Seleccionar factura</option>
            {originInvoices.map((invoice) => {
              const companyId = form.direction === 'sales'
                ? invoice.cliente_id
                : invoice.proveedor_id;
              const number = formatInvoiceNumber(invoice);
              const companyName = companyNames.get(companyId)
                || (form.direction === 'sales' ? 'Cliente' : 'Proveedor');

              return (
                <option key={invoice.id} value={invoice.id}>
                  {number} · {companyName} · {currency.format(Number(invoice.monto_total) || 0)}
                </option>
              );
            })}
          </FormInput>
        </FormField>
        <FormField>
          <label htmlFor="note-letter">Letra</label>
          <FormInput
            as="select"
            id="note-letter"
            value={form.letter}
            onChange={(event) => setForm({ ...form, letter: event.target.value })}
            required
          >
            {INVOICE_LETTERS.map((letter) => (
              <option key={letter} value={letter}>{letter}</option>
            ))}
          </FormInput>
        </FormField>
        <FormField>
          <label htmlFor="note-point-of-sale">Punto de venta</label>
          <FormInput
            id="note-point-of-sale"
            type="number"
            min="0"
            value={form.pointOfSale}
            onChange={(event) => setForm({ ...form, pointOfSale: event.target.value })}
            required
          />
        </FormField>
        <FormField>
          <label htmlFor="note-number">Número de nota</label>
          <FormInput
            id="note-number"
            type="number"
            min="1"
            value={form.invoiceNumber}
            onChange={(event) => setForm({ ...form, invoiceNumber: event.target.value })}
            required
          />
        </FormField>
        <FormField>
          <label htmlFor="note-issue-date">Fecha de emisión</label>
          <FormInput
            id="note-issue-date"
            type="date"
            value={form.issueDate}
            onChange={(event) => setForm({ ...form, issueDate: event.target.value })}
            required
          />
        </FormField>
        {form.direction === 'sales' ? (
          <FormField>
            <label htmlFor="note-estimated-payment-date">Fecha estimada de cobro</label>
            <FormInput
              id="note-estimated-payment-date"
              type="date"
              value={form.estimatedPaymentDate}
              onChange={(event) => setForm({
                ...form,
                estimatedPaymentDate: event.target.value,
              })}
              required
            />
          </FormField>
        ) : (
          <FormField>
            <label htmlFor="note-due-date">Vencimiento (opcional)</label>
            <FormInput
              id="note-due-date"
              type="date"
              value={form.dueDate}
              onChange={(event) => setForm({ ...form, dueDate: event.target.value })}
            />
          </FormField>
        )}
        <FormField>
          <label htmlFor="note-cae">CAE (opcional)</label>
          <FormInput
            id="note-cae"
            value={form.cae}
            onChange={(event) => setForm({ ...form, cae: event.target.value })}
          />
        </FormField>
        <FormField>
          <label htmlFor="note-amount">Importe</label>
          <FormInput
            id="note-amount"
            type="number"
            min="0.01"
            step="0.01"
            value={form.totalAmount}
            onChange={(event) => setForm({ ...form, totalAmount: event.target.value })}
            required
          />
        </FormField>
      </FormGrid>
      {!isLoading && !originInvoices.length && (
        <EmptyState>
          No hay facturas formales disponibles para vincular en esta operación.
        </EmptyState>
      )}
      <Button
        type="submit"
        disabled={isLoading || isSubmitting || !originInvoices.length || !selectedOrigin}
      >
        <TbPlus aria-hidden="true" />
        {isSubmitting ? 'Guardando…' : 'Registrar nota'}
      </Button>
    </Form>
  );
};

export default InvoiceNotes;
