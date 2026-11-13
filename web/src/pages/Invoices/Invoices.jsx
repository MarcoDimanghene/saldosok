import { useCallback, useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  TbArrowDownLeft,
  TbArrowUpRight,
  TbEye,
  TbFileInvoice,
  TbPlus,
} from 'react-icons/tb';
import { Link } from 'react-router-dom';
import {
  Button,
  StatusBadge,
  StyledTable,
  TableCell,
  TableHeader,
  TableRow,
} from '../../component/ui/UIComponents';
import {
  completePendingPurchase,
  createPendingPurchase,
  createPurchaseInvoice,
  createSalesInvoice,
} from '../../services/invoiceService';
import { INVOICE_LETTERS, INVOICE_TYPE_LABELS } from '../../config/appConfig';
import {
  fetchCompanies,
  fetchDashboard,
  fetchPurchaseInvoices,
  fetchSalesInvoices,
} from '../../store';
import {
  ActionCell,
  ActionForm,
  EmptyState,
  Form,
  FormField,
  FormGrid,
  FormInput,
  FilterBar,
  FilterField,
  InvoiceList,
  InvoiceRowHeading,
  InvoiceViewButton,
  PageHeader,
  Panel,
  SectionHeading,
  StatusMessage,
  TabButton,
  Tabs,
} from './Invoices.styles';
import { filterInvoices } from './invoiceFilters';
import {
  addDaysToDate,
  companyTermDays,
  formatDateCountdown,
  formatInvoiceDate,
} from './invoiceDates';
import InvoiceNotes from './InvoiceNotes';
import InvoiceDetailsDialog from './InvoiceDetailsDialog';
import InvoiceMovementDialog from './InvoiceMovementDialog';

const today = new Date().toISOString().slice(0, 10);
const initialSalesForm = {
  issuer_id: '',
  receiver_id: '',
  letter: 'A',
  point_of_sale: '',
  invoice_number: '',
  issue_date: today,
  estimated_payment_date: today,
  total_amount: '',
};
const initialPurchaseForm = {
  supplier_id: '',
  receiver_id: '',
  concept: '',
  total_amount: '',
  due_date: today,
};
const initialFormalPurchaseForm = {
  issuer_id: '',
  receiver_id: '',
  letter: 'A',
  point_of_sale: '',
  invoice_number: '',
  cae: '',
  issue_date: today,
  due_date: today,
  concept: '',
  total_amount: '',
};

const currency = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 2,
});
const formatCurrency = (amount) => currency.format(Number(amount) || 0);
const invoiceNumberLabel = (invoice) => (
  `${invoice.letra || '—'} ${invoice.punto_venta ?? '—'}-${invoice.nro_factura ?? '—'}`
);
const linkedInvoiceNumber = (invoices, originId) => {
  const originInvoice = invoices.find((invoice) => invoice.id === originId);
  return originInvoice ? invoiceNumberLabel(originInvoice) : `#${originId}`;
};
const remainingBalance = (total, paid) => Math.max(Number(total || 0) - Number(paid || 0), 0);
const isAdjustmentNote = (invoice) => (
  invoice.tipo_comprobante === 'nota_credito'
  || invoice.tipo_comprobante === 'nota_debito'
);
const noteImpact = (invoice) => (
  `${invoice.tipo_comprobante === 'nota_credito' ? '-' : '+'}${formatCurrency(invoice.monto_total)}`
);
const initialInvoiceFilters = {
  status: 'all',
  dateFrom: '',
  dateTo: '',
  company: 'all',
};

const Invoices = () => {
  const dispatch = useDispatch();
  const {
    items: companies,
    status: companiesStatus,
    error: companiesError,
  } = useSelector((state) => state.companies);
  const {
    sales: salesInvoices,
    purchases: purchaseInvoices,
    salesStatus,
    purchasesStatus,
    salesError,
    purchasesError,
  } = useSelector((state) => state.invoices);
  const [tab, setTab] = useState('sales');
  const [salesForm, setSalesForm] = useState(initialSalesForm);
  const [purchaseForm, setPurchaseForm] = useState(initialPurchaseForm);
  const [formalPurchaseForm, setFormalPurchaseForm] = useState(initialFormalPurchaseForm);
  const [salesCollectionDays, setSalesCollectionDays] = useState('0');
  const [pendingPaymentDays, setPendingPaymentDays] = useState('0');
  const [formalPaymentDays, setFormalPaymentDays] = useState('0');
  const [purchaseMode, setPurchaseMode] = useState('pending');
  const [formalizing, setFormalizing] = useState(null);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [movementDialog, setMovementDialog] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState(null);
  const [invoiceFilters, setInvoiceFilters] = useState(initialInvoiceFilters);

  const issuers = useMemo(() => companies.filter((company) => company.es_emisor), [companies]);
  const clients = useMemo(() => companies.filter((company) => company.es_cliente), [companies]);
  const suppliers = useMemo(
    () => companies.filter((company) => company.es_proveedor),
    [companies],
  );
  const companyNames = useMemo(
    () => new Map(companies.map((company) => [company.id, company.razon_social])),
    [companies],
  );
  const filterCompanies = useMemo(() => {
    const availableCompanies = tab === 'purchases'
      ? [...suppliers, ...issuers]
      : [...issuers, ...clients];
    return [...new Map(availableCompanies.map((company) => [company.id, company])).values()];
  }, [clients, issuers, suppliers, tab]);
  const visibleInvoices = useMemo(
    () => filterInvoices(
      tab === 'purchases' ? purchaseInvoices : salesInvoices,
      invoiceFilters,
      tab === 'purchases' ? 'purchases' : 'sales',
    ),
    [invoiceFilters, purchaseInvoices, salesInvoices, tab],
  );
  const selectedInvoiceRecord = selectedInvoice
    ? (selectedInvoice.direction === 'sales' ? salesInvoices : purchaseInvoices)
      .find((invoice) => invoice.id === selectedInvoice.id) || selectedInvoice.invoice
    : null;

  const refreshSales = useCallback(async () => {
    await Promise.all([
      dispatch(fetchSalesInvoices({ force: true })),
      dispatch(fetchDashboard({ force: true })),
    ]);
  }, [dispatch]);

  const refreshPurchases = useCallback(async () => {
    await Promise.all([
      dispatch(fetchPurchaseInvoices({ force: true })),
      dispatch(fetchDashboard({ force: true })),
    ]);
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchCompanies());
    dispatch(fetchSalesInvoices());
    dispatch(fetchPurchaseInvoices());
  }, [dispatch]);

  const isLoading = (
    ['idle', 'loading'].includes(companiesStatus)
    ||
    ['idle', 'loading'].includes(salesStatus)
    || ['idle', 'loading'].includes(purchasesStatus)
  );
  const loadError = salesError || purchasesError;

  const handleSalesClientChange = (receiverId) => {
    const client = clients.find((company) => String(company.id) === receiverId);
    const days = String(companyTermDays(client, 'dias_cobro'));
    setSalesCollectionDays(days);
    setSalesForm((current) => ({
      ...current,
      receiver_id: receiverId,
      estimated_payment_date: addDaysToDate(current.issue_date, days),
    }));
  };

  const handleSalesIssueDateChange = (issueDate) => {
    setSalesForm((current) => ({
      ...current,
      issue_date: issueDate,
      estimated_payment_date: addDaysToDate(issueDate, salesCollectionDays),
    }));
  };

  const handleSalesCollectionDaysChange = (days) => {
    setSalesCollectionDays(days);
    setSalesForm((current) => ({
      ...current,
      estimated_payment_date: addDaysToDate(current.issue_date, days),
    }));
  };

  const handlePendingSupplierChange = (supplierId) => {
    const supplier = suppliers.find((company) => String(company.id) === supplierId);
    const days = String(companyTermDays(supplier, 'dias_pago'));
    setPendingPaymentDays(days);
    setPurchaseForm((current) => ({
      ...current,
      supplier_id: supplierId,
      due_date: addDaysToDate(today, days),
    }));
  };

  const handlePendingPaymentDaysChange = (days) => {
    setPendingPaymentDays(days);
    setPurchaseForm((current) => ({
      ...current,
      due_date: addDaysToDate(today, days),
    }));
  };

  const handleFormalSupplierChange = (issuerId) => {
    const supplier = suppliers.find((company) => String(company.id) === issuerId);
    const days = String(companyTermDays(supplier, 'dias_pago'));
    setFormalPaymentDays(days);
    setFormalPurchaseForm((current) => ({
      ...current,
      issuer_id: issuerId,
      due_date: addDaysToDate(current.issue_date, days),
    }));
  };

  const handleFormalIssueDateChange = (issueDate) => {
    setFormalPurchaseForm((current) => ({
      ...current,
      issue_date: issueDate,
      due_date: addDaysToDate(issueDate, formalPaymentDays),
    }));
  };

  const handleFormalPaymentDaysChange = (days) => {
    setFormalPaymentDays(days);
    setFormalPurchaseForm((current) => ({
      ...current,
      due_date: addDaysToDate(current.issue_date, days),
    }));
  };

  const handleCreateSales = async (event) => {
    event.preventDefault();
    setMessage(null);
    setIsSubmitting(true);
    try {
      await createSalesInvoice({
        ...salesForm,
        issuer_id: Number(salesForm.issuer_id),
        receiver_id: Number(salesForm.receiver_id),
        point_of_sale: Number(salesForm.point_of_sale),
        invoice_number: Number(salesForm.invoice_number),
        total_amount: salesForm.total_amount,
      });
      setSalesForm({ ...initialSalesForm, issue_date: today, estimated_payment_date: today });
      setSalesCollectionDays('0');
      setMessage({ error: false, text: 'La factura de venta se registró correctamente.' });
      await refreshSales();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo registrar la factura.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreatePendingPurchase = async (event) => {
    event.preventDefault();
    setMessage(null);
    setIsSubmitting(true);
    try {
      const purchase = await createPendingPurchase({
        ...purchaseForm,
        supplier_id: Number(purchaseForm.supplier_id),
        receiver_id: Number(purchaseForm.receiver_id),
        total_amount: purchaseForm.total_amount,
        due_date: purchaseForm.due_date || null,
      });
      setPurchaseForm(initialPurchaseForm);
      setPendingPaymentDays('0');
      setMessage({
        error: false,
        text: `Compra creada con número interno ${purchase.numero_interno}.`,
      });
      await refreshPurchases();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo registrar la compra.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreatePurchaseInvoice = async (event) => {
    event.preventDefault();
    setMessage(null);
    setIsSubmitting(true);
    try {
      await createPurchaseInvoice({
        ...formalPurchaseForm,
        issuer_id: Number(formalPurchaseForm.issuer_id),
        receiver_id: Number(formalPurchaseForm.receiver_id),
        point_of_sale: Number(formalPurchaseForm.point_of_sale),
        invoice_number: Number(formalPurchaseForm.invoice_number),
        total_amount: formalPurchaseForm.total_amount,
        due_date: formalPurchaseForm.due_date || null,
        cae: formalPurchaseForm.cae.trim() || null,
        concept: formalPurchaseForm.concept.trim() || null,
      });
      setFormalPurchaseForm(initialFormalPurchaseForm);
      setFormalPaymentDays('0');
      setMessage({ error: false, text: 'La factura de compra se registró correctamente.' });
      await refreshPurchases();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo registrar la factura de compra.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCompletePurchase = async (event, invoiceId) => {
    event.preventDefault();
    setMessage(null);
    setIsSubmitting(true);
    const fields = new FormData(event.currentTarget);
    try {
      await completePendingPurchase(invoiceId, {
        letter: fields.get('letter'),
        point_of_sale: Number(fields.get('point_of_sale')),
        invoice_number: Number(fields.get('invoice_number')),
        issue_date: fields.get('issue_date'),
        total_amount: fields.get('total_amount'),
        due_date: fields.get('due_date') || null,
        cae: fields.get('cae') || null,
      });
      setFormalizing(null);
      setMessage({ error: false, text: 'Se agregaron los datos de la factura formal.' });
      await refreshPurchases();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo completar la factura.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectTab = (nextTab) => {
    setTab(nextTab);
    setSelectedInvoice(null);
    setMovementDialog(null);
    setFormalizing(null);
  };

  const closeInvoiceDetails = useCallback(() => setSelectedInvoice(null), []);
  const closeMovementDialog = useCallback(() => setMovementDialog(null), []);
  const refreshInvoiceData = useCallback(async (direction) => {
    await (direction === 'sales' ? refreshSales() : refreshPurchases());
  }, [refreshPurchases, refreshSales]);
  const handleMovementCreated = useCallback(async (direction) => {
    setMovementDialog(null);
    setMessage({
      error: false,
      text: direction === 'sales' ? 'Cobro registrado.' : 'Pago registrado.',
    });
    await refreshInvoiceData(direction);
  }, [refreshInvoiceData]);

  return (
    <>
      <PageHeader>
        <h1>Ventas, compras y notas</h1>
        <p>
          Registra facturas, notas de crédito y débito, compras pendientes y movimientos de cobro y pago.
          Usa el botón del ojo para abrir el detalle de una factura.
        </p>
      </PageHeader>

      {message && (
        <StatusMessage $error={message.error} role={message.error ? 'alert' : 'status'}>
          {message.text}
        </StatusMessage>
      )}
      {loadError && (
        <StatusMessage $error role="alert">{loadError}</StatusMessage>
      )}
      {companiesError && (
        <StatusMessage $error role="alert">{companiesError}</StatusMessage>
      )}

      <Tabs role="tablist" aria-label="Tipo de movimiento">
        <TabButton
          type="button"
          role="tab"
          aria-selected={tab === 'sales'}
          $active={tab === 'sales'}
          onClick={() => selectTab('sales')}
        >
          <TbArrowUpRight aria-hidden="true" /> Ventas
        </TabButton>
        <TabButton
          type="button"
          role="tab"
          aria-selected={tab === 'purchases'}
          $active={tab === 'purchases'}
          onClick={() => selectTab('purchases')}
        >
          <TbArrowDownLeft aria-hidden="true" /> Compras
        </TabButton>
        <TabButton
          type="button"
          role="tab"
          aria-selected={tab === 'notes'}
          $active={tab === 'notes'}
          onClick={() => selectTab('notes')}
        >
          <TbFileInvoice aria-hidden="true" /> Notas
        </TabButton>
      </Tabs>

      {tab === 'notes' ? (
        <Panel as="section">
          <SectionHeading>
            <h2>Nueva nota de crédito o débito</h2>
            <span>Vincula cada nota a una factura formal de venta o compra.</span>
          </SectionHeading>
          <InvoiceNotes
            companies={companies}
            salesInvoices={salesInvoices}
            purchaseInvoices={purchaseInvoices}
            isLoading={isLoading}
            onCreated={(direction) => (
              direction === 'sales' ? refreshSales() : refreshPurchases()
            )}
          />
        </Panel>
      ) : tab === 'sales' ? (
        <Panel as="section">
          <SectionHeading>
            <h2>Nueva factura de venta</h2>
            <span>Cada venta queda asociada a su empresa emisora.</span>
          </SectionHeading>
          {!issuers.length || !clients.length ? (
            <EmptyState>
              Para emitir una venta, registra al menos una empresa con rol «Emite ventas» y un
              cliente en <Link to="/companies">Empresas</Link>.
            </EmptyState>
          ) : (
            <Form onSubmit={handleCreateSales}>
              <FormGrid>
                <FormField>
                  <label htmlFor="sales-issuer">Empresa emisora</label>
                  <FormInput
                    as="select"
                    id="sales-issuer"
                    value={salesForm.issuer_id}
                    onChange={(event) => setSalesForm({ ...salesForm, issuer_id: event.target.value })}
                    required
                  >
                    <option value="">Seleccionar empresa</option>
                    {issuers.map((company) => (
                      <option key={company.id} value={company.id}>{company.razon_social}</option>
                    ))}
                  </FormInput>
                </FormField>
                <FormField>
                  <label htmlFor="sales-client">Cliente</label>
                  <FormInput
                    as="select"
                    id="sales-client"
                    value={salesForm.receiver_id}
                    onChange={(event) => handleSalesClientChange(event.target.value)}
                    required
                  >
                    <option value="">Seleccionar cliente</option>
                    {clients.map((company) => (
                      <option key={company.id} value={company.id}>{company.razon_social}</option>
                    ))}
                  </FormInput>
                </FormField>
                <FormField>
                  <label htmlFor="sales-letter">Letra</label>
                  <FormInput
                    as="select"
                    id="sales-letter"
                    value={salesForm.letter}
                    onChange={(event) => setSalesForm({ ...salesForm, letter: event.target.value })}
                    required
                  >
                    {INVOICE_LETTERS.map((letter) => (
                      <option key={letter} value={letter}>{letter}</option>
                    ))}
                  </FormInput>
                </FormField>
                <FormField>
                  <label htmlFor="sales-pos">Punto de venta</label>
                  <FormInput id="sales-pos" type="number" min="0" value={salesForm.point_of_sale} onChange={(event) => setSalesForm({ ...salesForm, point_of_sale: event.target.value })} required />
                </FormField>
                <FormField>
                  <label htmlFor="sales-number">Número de factura</label>
                  <FormInput id="sales-number" type="number" min="1" value={salesForm.invoice_number} onChange={(event) => setSalesForm({ ...salesForm, invoice_number: event.target.value })} required />
                </FormField>
                <FormField>
                  <label htmlFor="sales-amount">Importe</label>
                  <FormInput id="sales-amount" type="number" min="0.01" step="0.01" value={salesForm.total_amount} onChange={(event) => setSalesForm({ ...salesForm, total_amount: event.target.value })} required />
                </FormField>
                <FormField>
                  <label htmlFor="sales-collection-days">Plazo de cobro (días)</label>
                  <FormInput
                    id="sales-collection-days"
                    type="number"
                    min="0"
                    step="1"
                    value={salesCollectionDays}
                    onChange={(event) => handleSalesCollectionDaysChange(event.target.value)}
                    required
                  />
                </FormField>
                <FormField>
                  <label htmlFor="sales-date">Fecha de emisión</label>
                  <FormInput
                    id="sales-date"
                    type="date"
                    value={salesForm.issue_date}
                    onChange={(event) => handleSalesIssueDateChange(event.target.value)}
                    required
                  />
                </FormField>
                <FormField>
                  <label htmlFor="sales-due-date">Fecha estimada de cobro (automática)</label>
                  <FormInput
                    id="sales-due-date"
                    type="date"
                    value={salesForm.estimated_payment_date}
                    readOnly
                    required
                  />
                </FormField>
              </FormGrid>
              <Button type="submit" disabled={isSubmitting}>
                <TbPlus aria-hidden="true" /> Crear factura
              </Button>
            </Form>
          )}
        </Panel>
      ) : (
        <Panel as="section">
          <SectionHeading>
            <h2>Registrar una compra</h2>
            <span>Registra la factura recibida o carga la compra mientras esperas el comprobante.</span>
          </SectionHeading>
          {!suppliers.length || !issuers.length ? (
            <EmptyState>
              Registra un proveedor y una empresa destinataria habilitada como emisora en{' '}
              <Link to="/companies">Empresas</Link> antes de cargar una compra.
            </EmptyState>
          ) : (
            <>
              <Tabs role="tablist" aria-label="Estado de la factura de compra">
                <TabButton
                  type="button"
                  role="tab"
                  aria-selected={purchaseMode === 'pending'}
                  $active={purchaseMode === 'pending'}
                  onClick={() => setPurchaseMode('pending')}
                >
                  Compra sin factura
                </TabButton>
                <TabButton
                  type="button"
                  role="tab"
                  aria-selected={purchaseMode === 'formal'}
                  $active={purchaseMode === 'formal'}
                  onClick={() => setPurchaseMode('formal')}
                >
                  Compra con factura
                </TabButton>
              </Tabs>
              {purchaseMode === 'pending' ? (
                <Form onSubmit={handleCreatePendingPurchase}>
                  <FormGrid>
                    <FormField>
                      <label htmlFor="purchase-supplier">Proveedor</label>
                      <FormInput
                        as="select"
                        id="purchase-supplier"
                        value={purchaseForm.supplier_id}
                        onChange={(event) => handlePendingSupplierChange(event.target.value)}
                        required
                      >
                        <option value="">Seleccionar proveedor</option>
                        {suppliers.map((company) => (
                          <option key={company.id} value={company.id}>{company.razon_social}</option>
                        ))}
                      </FormInput>
                    </FormField>
                    <FormField>
                      <label htmlFor="purchase-recipient">Empresa destinataria</label>
                      <FormInput
                        as="select"
                        id="purchase-recipient"
                        value={purchaseForm.receiver_id}
                        onChange={(event) => setPurchaseForm({
                          ...purchaseForm,
                          receiver_id: event.target.value,
                        })}
                        required
                      >
                        <option value="">Seleccionar empresa</option>
                        {issuers.map((company) => (
                          <option key={company.id} value={company.id}>{company.razon_social}</option>
                        ))}
                      </FormInput>
                    </FormField>
                    <FormField>
                      <label htmlFor="purchase-concept">Concepto</label>
                      <FormInput id="purchase-concept" value={purchaseForm.concept} onChange={(event) => setPurchaseForm({ ...purchaseForm, concept: event.target.value })} maxLength="300" required />
                    </FormField>
                    <FormField>
                      <label htmlFor="purchase-amount">Importe de la obligación</label>
                      <FormInput id="purchase-amount" type="number" min="0.01" step="0.01" value={purchaseForm.total_amount} onChange={(event) => setPurchaseForm({ ...purchaseForm, total_amount: event.target.value })} required />
                    </FormField>
                    <FormField>
                      <label htmlFor="purchase-payment-days">Plazo para pagar (días)</label>
                      <FormInput
                        id="purchase-payment-days"
                        type="number"
                        min="0"
                        step="1"
                        value={pendingPaymentDays}
                        onChange={(event) => handlePendingPaymentDaysChange(event.target.value)}
                        required
                      />
                    </FormField>
                    <FormField>
                      <label htmlFor="purchase-due-date">Vencimiento estimado (automático)</label>
                      <FormInput
                        id="purchase-due-date"
                        type="date"
                        value={purchaseForm.due_date}
                        readOnly
                      />
                    </FormField>
                  </FormGrid>
                  <Button type="submit" disabled={isSubmitting}>
                    <TbPlus aria-hidden="true" /> {isSubmitting ? 'Guardando…' : 'Registrar compra sin factura'}
                  </Button>
                </Form>
              ) : (
                <Form onSubmit={handleCreatePurchaseInvoice}>
                  <FormGrid>
                    <FormField>
                      <label htmlFor="formal-purchase-supplier">Proveedor</label>
                      <FormInput
                        as="select"
                        id="formal-purchase-supplier"
                        value={formalPurchaseForm.issuer_id}
                        onChange={(event) => handleFormalSupplierChange(event.target.value)}
                        required
                      >
                        <option value="">Seleccionar proveedor</option>
                        {suppliers.map((company) => (
                          <option key={company.id} value={company.id}>{company.razon_social}</option>
                        ))}
                      </FormInput>
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-recipient">Empresa destinataria</label>
                      <FormInput
                        as="select"
                        id="formal-purchase-recipient"
                        value={formalPurchaseForm.receiver_id}
                        onChange={(event) => setFormalPurchaseForm({
                          ...formalPurchaseForm,
                          receiver_id: event.target.value,
                        })}
                        required
                      >
                        <option value="">Seleccionar empresa</option>
                        {issuers.map((company) => (
                          <option key={company.id} value={company.id}>{company.razon_social}</option>
                        ))}
                      </FormInput>
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-concept">Concepto (opcional)</label>
                      <FormInput id="formal-purchase-concept" value={formalPurchaseForm.concept} onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, concept: event.target.value })} maxLength="300" />
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-letter">Letra</label>
                      <FormInput
                        as="select"
                        id="formal-purchase-letter"
                        value={formalPurchaseForm.letter}
                        onChange={(event) => setFormalPurchaseForm({
                          ...formalPurchaseForm,
                          letter: event.target.value,
                        })}
                        required
                      >
                        {INVOICE_LETTERS.map((letter) => (
                          <option key={letter} value={letter}>{letter}</option>
                        ))}
                      </FormInput>
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-pos">Punto de venta</label>
                      <FormInput id="formal-purchase-pos" type="number" min="0" value={formalPurchaseForm.point_of_sale} onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, point_of_sale: event.target.value })} required />
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-number">Número de factura</label>
                      <FormInput id="formal-purchase-number" type="number" min="1" value={formalPurchaseForm.invoice_number} onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, invoice_number: event.target.value })} required />
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-cae">CAE (opcional)</label>
                      <FormInput id="formal-purchase-cae" value={formalPurchaseForm.cae} onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, cae: event.target.value })} />
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-date">Fecha de emisión</label>
                      <FormInput
                        id="formal-purchase-date"
                        type="date"
                        value={formalPurchaseForm.issue_date}
                        onChange={(event) => handleFormalIssueDateChange(event.target.value)}
                        required
                      />
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-payment-days">Plazo para pagar (días)</label>
                      <FormInput
                        id="formal-purchase-payment-days"
                        type="number"
                        min="0"
                        step="1"
                        value={formalPaymentDays}
                        onChange={(event) => handleFormalPaymentDaysChange(event.target.value)}
                        required
                      />
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-due-date">Vencimiento estimado (automático)</label>
                      <FormInput
                        id="formal-purchase-due-date"
                        type="date"
                        value={formalPurchaseForm.due_date}
                        readOnly
                      />
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-amount">Importe</label>
                      <FormInput id="formal-purchase-amount" type="number" min="0.01" step="0.01" value={formalPurchaseForm.total_amount} onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, total_amount: event.target.value })} required />
                    </FormField>
                  </FormGrid>
                  <Button type="submit" disabled={isSubmitting}>
                    <TbPlus aria-hidden="true" /> {isSubmitting ? 'Guardando…' : 'Registrar factura de compra'}
                  </Button>
                </Form>
              )}
            </>
          )}
        </Panel>
      )}

      {tab !== 'notes' && (
      <Panel as="section">
        <SectionHeading>
          <h2>{tab === 'sales' ? 'Facturas de venta' : 'Compras y facturas de proveedor'}</h2>
          <span>
            {isLoading
              ? 'Cargando…'
              : `${visibleInvoices.length} de ${tab === 'sales' ? salesInvoices.length : purchaseInvoices.length} registros`}
          </span>
        </SectionHeading>
        <FilterBar aria-label="Filtros de facturas">
          <FilterField>
            Estado
            <FormInput
              as="select"
              value={invoiceFilters.status}
              onChange={(event) => setInvoiceFilters({
                ...invoiceFilters,
                status: event.target.value,
              })}
            >
              <option value="all">Todos</option>
              <option value="pendiente">Pendiente</option>
              <option value="parcial">Parcial</option>
              <option value="pagado">{tab === 'sales' ? 'Cobrado' : 'Pagado'}</option>
              <option value="vencida">Vencida</option>
            </FormInput>
          </FilterField>
          <FilterField>
            Desde
            <FormInput
              type="date"
              value={invoiceFilters.dateFrom}
              onChange={(event) => setInvoiceFilters({
                ...invoiceFilters,
                dateFrom: event.target.value,
              })}
            />
          </FilterField>
          <FilterField>
            Hasta
            <FormInput
              type="date"
              value={invoiceFilters.dateTo}
              onChange={(event) => setInvoiceFilters({
                ...invoiceFilters,
                dateTo: event.target.value,
              })}
            />
          </FilterField>
          <FilterField>
            Empresa
            <FormInput
              as="select"
              value={invoiceFilters.company}
              onChange={(event) => setInvoiceFilters({
                ...invoiceFilters,
                company: event.target.value,
              })}
            >
              <option value="all">Todas</option>
              {filterCompanies.map((company) => (
                <option key={company.id} value={company.id}>{company.razon_social}</option>
              ))}
            </FormInput>
          </FilterField>
          <Button
            type="button"
            $variant="secondary"
            onClick={() => setInvoiceFilters(initialInvoiceFilters)}
            disabled={Object.entries(initialInvoiceFilters).every(
              ([key, value]) => invoiceFilters[key] === value,
            )}
          >
            Limpiar
          </Button>
        </FilterBar>
        {isLoading ? (
          <p role="status">Cargando movimientos…</p>
        ) : tab === 'sales' ? (
          <InvoiceList>
            <StyledTable>
              <thead>
                <tr>
                  <TableHeader>Factura</TableHeader>
                  <TableHeader>Emisor / destinatario</TableHeader>
                  <TableHeader>Importe</TableHeader>
                  <TableHeader>Estado</TableHeader>
                  <TableHeader>Acciones</TableHeader>
                </tr>
              </thead>
              <tbody>
                {visibleInvoices.map((invoice) => (
                  <TableRow
                    key={invoice.id}
                    className={invoice.estado === 'pendiente' ? 'invoice-row--pending' : undefined}
                  >
                    <TableCell>
                      <InvoiceRowHeading>
                        <div>
                          <strong>
                            {INVOICE_TYPE_LABELS[invoice.tipo_comprobante] || 'Factura'}{' '}
                            {invoiceNumberLabel(invoice)}
                          </strong>
                        </div>
                        <InvoiceViewButton
                          type="button"
                          aria-label={`Ver detalle de factura ${invoiceNumberLabel(invoice)}`}
                          title="Ver detalle de factura"
                          onClick={() => setSelectedInvoice({
                            direction: 'sales',
                            id: invoice.id,
                            invoice,
                          })}
                        >
                          <TbEye aria-hidden="true" />
                        </InvoiceViewButton>
                      </InvoiceRowHeading>
                      {invoice.factura_origen_id && (
                        <span>
                          Vinculada a: {linkedInvoiceNumber(salesInvoices, invoice.factura_origen_id)}
                        </span>
                      )}
                      {invoice.fecha_pago_approx && (
                        <>
                          <span>Fecha aprox. de cobro: {formatInvoiceDate(invoice.fecha_pago_approx)}</span>
                          <span className="invoice-date-countdown">
                            {formatDateCountdown(invoice.fecha_pago_approx, 'collection')}
                          </span>
                        </>
                      )}
                    </TableCell>
                    <TableCell>
                      {companyNames.get(invoice.emisor_id) || 'Emisor anterior'}
                      <span>
                        Destinatario: {companyNames.get(invoice.cliente_id) || 'Cliente'}
                      </span>
                    </TableCell>
                    <TableCell className="numeric">
                      {formatCurrency(invoice.monto_total)}
                      {isAdjustmentNote(invoice) ? (
                        <span>Impacto en comprobante: {noteImpact(invoice)}</span>
                      ) : (
                        <>
                          {Number(invoice.monto_ajustado) !== Number(invoice.monto_total) && (
                            <>
                              <span>Importe original: {formatCurrency(invoice.monto_total)}</span>
                              <span>Total tras notas: {formatCurrency(invoice.monto_ajustado)}</span>
                            </>
                          )}
                          <span>
                            Saldo pendiente: {formatCurrency(
                              invoice.saldo_pendiente
                              ?? remainingBalance(invoice.monto_ajustado ?? invoice.monto_total, invoice.monto_cobrado),
                            )}
                          </span>
                        </>
                      )}
                    </TableCell>
                    <TableCell>
                      <StatusBadge
                        className={!isAdjustmentNote(invoice) && invoice.estado === 'pendiente'
                          ? 'invoice-status--pending'
                          : !isAdjustmentNote(invoice) && invoice.estado === 'pagado' ? 'invoice-status--settled' : undefined}
                        $status={invoice.estado === 'pagado' ? 'saldada' : invoice.estado === 'vencida' ? 'vencida' : 'pendiente'}
                      >
                        {isAdjustmentNote(invoice)
                          ? 'Aplicada'
                          : invoice.estado === 'pagado' ? 'Cobrado' : invoice.estado || 'pendiente'}
                      </StatusBadge>
                    </TableCell>
                    <TableCell>
                      <ActionCell>
                        <Button
                          type="button"
                          $variant="secondary"
                          onClick={() => {
                            setMessage(null);
                            setSelectedInvoice(null);
                            setFormalizing(null);
                            setMovementDialog({ direction: 'sales', invoice });
                          }}
                          disabled={isAdjustmentNote(invoice) || invoice.estado === 'pagado' || isSubmitting}
                        >
                          {isAdjustmentNote(invoice) ? 'Nota aplicada' : 'Registrar cobro'}
                        </Button>
                      </ActionCell>
                    </TableCell>
                  </TableRow>
                ))}
              </tbody>
            </StyledTable>
            {!visibleInvoices.length && (
              <EmptyState>
                {salesInvoices.length
                  ? 'No hay facturas que coincidan con los filtros.'
                  : 'Aún no hay facturas de venta.'}
              </EmptyState>
            )}
          </InvoiceList>
        ) : (
          <InvoiceList>
            <StyledTable>
              <thead>
                <tr>
                  <TableHeader>Registro</TableHeader>
                  <TableHeader>Proveedor / destinatario</TableHeader>
                  <TableHeader>Importe</TableHeader>
                  <TableHeader>Estado</TableHeader>
                  <TableHeader>Acciones</TableHeader>
                </tr>
              </thead>
              <tbody>
                {visibleInvoices.map((invoice) => (
                  <TableRow
                    key={invoice.id}
                    className={invoice.estado === 'pendiente' ? 'invoice-row--pending' : undefined}
                  >
                    <TableCell>
                      <InvoiceRowHeading>
                        <div>
                          <strong>{invoice.numero_interno || `Compra ${invoice.id}`}</strong>
                          <span>
                            {invoice.factura_recibida
                              ? `${INVOICE_TYPE_LABELS[invoice.tipo_comprobante] || 'Factura'} ${invoiceNumberLabel(invoice)}`
                              : 'Factura formal pendiente'}
                          </span>
                        </div>
                        <InvoiceViewButton
                          type="button"
                          aria-label={`Ver detalle de compra ${invoice.numero_interno || invoiceNumberLabel(invoice)}`}
                          title="Ver detalle de compra"
                          onClick={() => setSelectedInvoice({
                            direction: 'purchases',
                            id: invoice.id,
                            invoice,
                          })}
                        >
                          <TbEye aria-hidden="true" />
                        </InvoiceViewButton>
                      </InvoiceRowHeading>
                      {invoice.factura_origen_id && (
                        <span>
                          Vinculada a: {linkedInvoiceNumber(purchaseInvoices, invoice.factura_origen_id)}
                        </span>
                      )}
                      {invoice.fecha_vencimiento && (
                        <>
                          <span>Vencimiento: {formatInvoiceDate(invoice.fecha_vencimiento)}</span>
                          <span className={`invoice-date-countdown${formatDateCountdown(invoice.fecha_vencimiento, 'due')?.startsWith('Vencida') ? ' invoice-date-countdown--overdue' : ''}`}>
                            {formatDateCountdown(invoice.fecha_vencimiento, 'due')}
                          </span>
                        </>
                      )}
                    </TableCell>
                    <TableCell>
                      {companyNames.get(invoice.proveedor_id) || 'Proveedor'}
                      <span>
                        Destinatario: {companyNames.get(invoice.receptor_id) || 'Sin destinatario registrado'}
                      </span>
                      {invoice.concepto && <span>{invoice.concepto}</span>}
                    </TableCell>
                    <TableCell className="numeric">
                      {formatCurrency(invoice.monto_total)}
                      {isAdjustmentNote(invoice) ? (
                        <span>Impacto en comprobante: {noteImpact(invoice)}</span>
                      ) : (
                        <>
                          {Number(invoice.monto_ajustado) !== Number(invoice.monto_total) && (
                            <>
                              <span>Importe original: {formatCurrency(invoice.monto_total)}</span>
                              <span>Total tras notas: {formatCurrency(invoice.monto_ajustado)}</span>
                            </>
                          )}
                          <span>
                            Saldo pendiente: {formatCurrency(
                              invoice.saldo_pendiente
                              ?? remainingBalance(invoice.monto_ajustado ?? invoice.monto_total, invoice.monto_pagado),
                            )}
                          </span>
                        </>
                      )}
                    </TableCell>
                    <TableCell>
                      <StatusBadge
                        className={!isAdjustmentNote(invoice) && invoice.estado === 'pendiente'
                          ? 'invoice-status--pending'
                          : !isAdjustmentNote(invoice) && invoice.estado === 'pagado' ? 'invoice-status--settled' : undefined}
                        $status={invoice.estado === 'pagado' ? 'saldada' : invoice.estado === 'vencida' ? 'vencida' : 'pendiente'}
                      >
                        {isAdjustmentNote(invoice) ? 'Aplicada' : invoice.estado || 'pendiente'}
                      </StatusBadge>
                    </TableCell>
                    <TableCell>
                      <ActionCell>
                        <Button
                          type="button"
                          $variant="secondary"
                          onClick={() => {
                            setMessage(null);
                            setSelectedInvoice(null);
                            setFormalizing(null);
                            setMovementDialog({ direction: 'purchases', invoice });
                          }}
                          disabled={isAdjustmentNote(invoice) || invoice.estado === 'pagado' || isSubmitting}
                        >
                          {isAdjustmentNote(invoice) ? 'Nota aplicada' : 'Registrar pago'}
                        </Button>
                        {!invoice.factura_recibida && (
                          <Button type="button" $variant="secondary" onClick={() => {
                            setFormalizing(formalizing?.id === invoice.id ? null : invoice);
                          }}>
                            <TbFileInvoice aria-hidden="true" /> Completar factura
                          </Button>
                        )}
                        {formalizing?.id === invoice.id && (
                          <ActionForm onSubmit={(event) => handleCompletePurchase(event, invoice.id)}>
                            <FormInput as="select" name="letter" aria-label="Letra" required>
                              {INVOICE_LETTERS.map((letter) => (
                                <option key={letter} value={letter}>{letter}</option>
                              ))}
                            </FormInput>
                            <FormInput name="point_of_sale" type="number" min="0" placeholder="Punto de venta" aria-label="Punto de venta" required />
                            <FormInput name="invoice_number" type="number" min="1" placeholder="Número" aria-label="Número de factura" required />
                            <FormInput name="issue_date" type="date" aria-label="Fecha de emisión" required />
                            <FormInput name="due_date" type="date" defaultValue={invoice.fecha_vencimiento || ''} aria-label="Fecha de vencimiento" />
                            <FormInput name="cae" placeholder="CAE (opcional)" aria-label="CAE (opcional)" />
                            <FormInput name="total_amount" type="number" min="0.01" step="0.01" defaultValue={formalizing.monto_total} aria-label="Importe formal de la factura" required />
                            <Button type="submit" disabled={isSubmitting}>Guardar factura</Button>
                          </ActionForm>
                        )}
                      </ActionCell>
                    </TableCell>
                  </TableRow>
                ))}
              </tbody>
            </StyledTable>
            {!visibleInvoices.length && (
              <EmptyState>
                {purchaseInvoices.length
                  ? 'No hay compras que coincidan con los filtros.'
                  : 'Aún no hay compras registradas.'}
              </EmptyState>
            )}
          </InvoiceList>
        )}
      </Panel>
      )}
      {selectedInvoiceRecord && selectedInvoice && (
        <InvoiceDetailsDialog
          key={`${selectedInvoice.direction}-${selectedInvoice.id}`}
          invoice={selectedInvoiceRecord}
          direction={selectedInvoice.direction}
          companies={companies}
          companyNames={companyNames}
          salesInvoices={salesInvoices}
          purchaseInvoices={purchaseInvoices}
          onClose={closeInvoiceDetails}
          onUpdated={refreshInvoiceData}
        />
      )}
      {movementDialog && (
        <InvoiceMovementDialog
          key={`${movementDialog.direction}-${movementDialog.invoice.id}`}
          direction={movementDialog.direction}
          invoice={movementDialog.invoice}
          onClose={closeMovementDialog}
          onCreated={handleMovementCreated}
        />
      )}
    </>
  );
};

export default Invoices;
