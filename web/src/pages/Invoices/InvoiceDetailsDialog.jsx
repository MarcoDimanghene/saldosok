import { useEffect, useRef, useState } from 'react';
import { Button } from '../../component/ui/UIComponents';
import { INVOICE_TYPE_LABELS } from '../../config/appConfig';
import { updatePurchaseInvoice } from '../../services/invoiceService';
import { formatInvoiceDate } from './invoiceDates';
import InvoiceMovementEditor from './InvoiceMovementEditor';
import InvoiceNotes from './InvoiceNotes';
import {
  EmptyState,
  Form,
  FormField,
  FormInput,
  InvoiceDetailGrid,
  InvoiceDetailItem,
  InvoiceDialog,
  InvoiceDialogContent,
  SectionHeading,
  StatusMessage,
} from './Invoices.styles';

const currency = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 2,
});
const invoiceNumberLabel = (invoice) => (
  `${invoice.letra || '—'} ${invoice.punto_venta ?? '—'}-${invoice.nro_factura ?? '—'}`
);

const InvoiceDetailsDialog = ({
  invoice,
  direction,
  companies,
  companyNames,
  salesInvoices,
  purchaseInvoices,
  onClose,
  onUpdated,
}) => {
  const dialogRef = useRef(null);
  const [showNoteForm, setShowNoteForm] = useState(false);
  const [editingRecipient, setEditingRecipient] = useState(false);
  const [recipientId, setRecipientId] = useState(String(invoice.receptor_id || ''));
  const [recipientError, setRecipientError] = useState(null);
  const [recipientSaving, setRecipientSaving] = useState(false);
  const isSales = direction === 'sales';
  const isFormalPurchase = isSales || invoice.factura_recibida;
  const invoiceType = INVOICE_TYPE_LABELS[invoice.tipo_comprobante] || 'Factura';
  const title = invoice.factura_recibida === false
    ? invoice.numero_interno || `Compra ${invoice.id}`
    : `${invoiceType} ${invoiceNumberLabel(invoice)}`;
  const relatedInvoices = isSales ? salesInvoices : purchaseInvoices;
  const originInvoice = relatedInvoices.find(
    (item) => item.id === invoice.factura_origen_id,
  );
  const paidAmount = Number(isSales ? invoice.monto_cobrado : invoice.monto_pagado) || 0;
  const outstandingAmount = Math.max(Number(invoice.monto_total || 0) - paidAmount, 0);
  const recipient = isSales
    ? companyNames.get(invoice.cliente_id) || 'Cliente no encontrado'
    : companyNames.get(invoice.receptor_id) || 'Sin empresa destinataria registrada';

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

  const handleRecipientUpdate = async (event) => {
    event.preventDefault();
    setRecipientError(null);
    setRecipientSaving(true);
    try {
      await updatePurchaseInvoice(invoice.id, { receiver_id: Number(recipientId) });
      setEditingRecipient(false);
      await onUpdated('purchases');
    } catch (error) {
      setRecipientError(
        error.message || 'No se pudo actualizar la empresa destinataria.',
      );
    } finally {
      setRecipientSaving(false);
    }
  };

  const handleDialogClick = (event) => {
    if (event.target === dialogRef.current) dialogRef.current.close();
  };

  return (
    <InvoiceDialog ref={dialogRef} onClick={handleDialogClick} aria-labelledby="invoice-details-title">
      <InvoiceDialogContent>
        <SectionHeading>
          <div>
            <h2 id="invoice-details-title">{title}</h2>
            <span>{invoiceType} · {isSales ? 'Venta' : 'Compra'}</span>
          </div>
          <Button type="button" $variant="secondary" onClick={() => dialogRef.current?.close()}>
            Cerrar
          </Button>
        </SectionHeading>

        <InvoiceDetailGrid>
          {isSales ? (
            <>
              <InvoiceDetailItem>
                <span>Empresa emisora</span>
                <strong>{companyNames.get(invoice.emisor_id) || 'Emisor anterior'}</strong>
              </InvoiceDetailItem>
              <InvoiceDetailItem>
                <span>Destinatario</span>
                <strong>{recipient}</strong>
              </InvoiceDetailItem>
            </>
          ) : (
            <>
              <InvoiceDetailItem>
                <span>Proveedor</span>
                <strong>{companyNames.get(invoice.proveedor_id) || 'Proveedor no encontrado'}</strong>
              </InvoiceDetailItem>
              <InvoiceDetailItem>
                <span>Destinatario</span>
                <strong>{recipient}</strong>
              </InvoiceDetailItem>
            </>
          )}
          <InvoiceDetailItem>
            <span>Importe</span>
            <strong>{currency.format(Number(invoice.monto_total) || 0)}</strong>
          </InvoiceDetailItem>
          <InvoiceDetailItem>
            <span>{isSales ? 'Cobrado' : 'Pagado'}</span>
            <strong>{currency.format(paidAmount)}</strong>
          </InvoiceDetailItem>
          <InvoiceDetailItem>
            <span>Saldo</span>
            <strong>{currency.format(outstandingAmount)}</strong>
          </InvoiceDetailItem>
          <InvoiceDetailItem>
            <span>Estado</span>
            <strong>{invoice.estado || 'pendiente'}</strong>
          </InvoiceDetailItem>
          <InvoiceDetailItem>
            <span>Fecha de emisión</span>
            <strong>{formatInvoiceDate(invoice.fecha_emision) || '—'}</strong>
          </InvoiceDetailItem>
          <InvoiceDetailItem>
            <span>{isSales ? 'Fecha estimada de cobro' : 'Vencimiento'}</span>
            <strong>
              {formatInvoiceDate(isSales
                ? invoice.fecha_pago_approx
                : invoice.fecha_vencimiento) || '—'}
            </strong>
          </InvoiceDetailItem>
          {invoice.cae && (
            <InvoiceDetailItem>
              <span>CAE</span>
              <strong>{invoice.cae}</strong>
            </InvoiceDetailItem>
          )}
          {invoice.concepto && (
            <InvoiceDetailItem>
              <span>Concepto</span>
              <strong>{invoice.concepto}</strong>
            </InvoiceDetailItem>
          )}
          {originInvoice && (
            <InvoiceDetailItem>
              <span>Comprobante relacionado</span>
              <strong>
                {INVOICE_TYPE_LABELS[originInvoice.tipo_comprobante] || 'Factura'}{' '}
                {invoiceNumberLabel(originInvoice)}
              </strong>
            </InvoiceDetailItem>
          )}
        </InvoiceDetailGrid>

        {!isSales && !invoice.receptor_id && (
          <section>
            <SectionHeading>
              <h3>Empresa destinataria</h3>
              <Button
                type="button"
                $variant="secondary"
                onClick={() => setEditingRecipient((current) => !current)}
              >
                {editingRecipient ? 'Cancelar' : 'Asignar empresa'}
              </Button>
            </SectionHeading>
            {editingRecipient && (
              <Form onSubmit={handleRecipientUpdate}>
                {recipientError && (
                  <StatusMessage $error role="alert">{recipientError}</StatusMessage>
                )}
                {companies.filter((company) => company.es_emisor).length ? (
                  <FormField>
                    <label htmlFor="invoice-recipient">Empresa destinataria</label>
                    <FormInput
                      as="select"
                      id="invoice-recipient"
                      value={recipientId}
                      onChange={(event) => setRecipientId(event.target.value)}
                      required
                    >
                      <option value="">Seleccionar empresa</option>
                      {companies.filter((company) => company.es_emisor).map((company) => (
                        <option key={company.id} value={company.id}>
                          {company.razon_social}
                        </option>
                      ))}
                    </FormInput>
                  </FormField>
                ) : (
                  <EmptyState>
                    Registra una empresa emisora en Empresas para asignar el destinatario.
                  </EmptyState>
                )}
                <Button
                  type="submit"
                  disabled={recipientSaving || !companies.some((company) => company.es_emisor)}
                >
                  {recipientSaving ? 'Guardando…' : 'Guardar destinatario'}
                </Button>
              </Form>
            )}
          </section>
        )}

        {isFormalPurchase && (!invoice.tipo_comprobante || invoice.tipo_comprobante === 'factura') && (
          <section>
            <SectionHeading>
              <h3>Notas de crédito y débito</h3>
              <Button
                type="button"
                $variant="secondary"
                onClick={() => setShowNoteForm((current) => !current)}
              >
                {showNoteForm ? 'Cerrar formulario' : 'Crear nota'}
              </Button>
            </SectionHeading>
            {showNoteForm && (
              <InvoiceNotes
                key={`${direction}-${invoice.id}`}
                companies={companies}
                salesInvoices={salesInvoices}
                purchaseInvoices={purchaseInvoices}
                isLoading={false}
                initialDirection={direction}
                originInvoice={invoice}
                onCreated={async (noteDirection) => {
                  await onUpdated(noteDirection);
                  setShowNoteForm(false);
                }}
              />
            )}
          </section>
        )}

        <section>
          <h3>Historial de {isSales ? 'cobros' : 'pagos'}</h3>
          <InvoiceMovementEditor
            direction={direction}
            invoiceId={invoice.id}
            onUpdated={() => onUpdated(direction)}
          />
        </section>
      </InvoiceDialogContent>
    </InvoiceDialog>
  );
};

export default InvoiceDetailsDialog;
