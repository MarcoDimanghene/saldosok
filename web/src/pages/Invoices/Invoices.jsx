import { useCallback, useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { TbArrowDownLeft, TbArrowUpRight, TbFileInvoice, TbPlus } from 'react-icons/tb';
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
import { createCollection, createPayment } from '../../services/paymentService';
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
  InvoiceList,
  PageHeader,
  Panel,
  SectionHeading,
  StatusMessage,
  TabButton,
  Tabs,
} from './Invoices.styles';

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
  concept: '',
  total_amount: '',
  due_date: '',
};
const initialFormalPurchaseForm = {
  issuer_id: '',
  letter: 'A',
  point_of_sale: '',
  invoice_number: '',
  cae: '',
  issue_date: today,
  due_date: '',
  concept: '',
  total_amount: '',
};

const currency = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 2,
});
const formatCurrency = (amount) => currency.format(Number(amount) || 0);

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
  const [purchaseMode, setPurchaseMode] = useState('pending');
  const [settlement, setSettlement] = useState(null);
  const [formalizing, setFormalizing] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

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
        total_amount: purchaseForm.total_amount,
        due_date: purchaseForm.due_date || null,
      });
      setPurchaseForm(initialPurchaseForm);
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
        point_of_sale: Number(formalPurchaseForm.point_of_sale),
        invoice_number: Number(formalPurchaseForm.invoice_number),
        total_amount: formalPurchaseForm.total_amount,
        due_date: formalPurchaseForm.due_date || null,
        cae: formalPurchaseForm.cae.trim() || null,
        concept: formalPurchaseForm.concept.trim() || null,
      });
      setFormalPurchaseForm(initialFormalPurchaseForm);
      setMessage({ error: false, text: 'La factura de compra se registró correctamente.' });
      await refreshPurchases();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo registrar la factura de compra.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSettlement = async (event, invoiceId, type) => {
    event.preventDefault();
    setMessage(null);
    setIsSubmitting(true);
    const amount = new FormData(event.currentTarget).get('amount');
    try {
      if (type === 'collection') {
        await createCollection({
          invoice_id: invoiceId,
          amount,
          collection_date: today,
        });
      } else {
        await createPayment({
          invoice_id: invoiceId,
          amount,
          payment_date: today,
        });
      }
      setSettlement(null);
      setMessage({
        error: false,
        text: type === 'collection' ? 'Cobro registrado.' : 'Pago registrado.',
      });
      await (type === 'collection' ? refreshSales() : refreshPurchases());
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo registrar el movimiento.' });
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

  const toggleSettlement = (invoiceId, type) => {
    setSettlement((current) => (
      current?.invoiceId === invoiceId && current.type === type ? null : { invoiceId, type }
    ));
    setFormalizing(null);
  };

  return (
    <>
      <PageHeader>
        <h1>Ventas y compras</h1>
        <p>Registra facturas, compras pendientes y movimientos parciales de cobro y pago.</p>
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
          onClick={() => setTab('sales')}
        >
          <TbArrowUpRight aria-hidden="true" /> Ventas
        </TabButton>
        <TabButton
          type="button"
          role="tab"
          aria-selected={tab === 'purchases'}
          $active={tab === 'purchases'}
          onClick={() => setTab('purchases')}
        >
          <TbArrowDownLeft aria-hidden="true" /> Compras
        </TabButton>
      </Tabs>

      {tab === 'sales' ? (
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
                    onChange={(event) => setSalesForm({ ...salesForm, receiver_id: event.target.value })}
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
                  <FormInput id="sales-letter" value={salesForm.letter} maxLength="1" onChange={(event) => setSalesForm({ ...salesForm, letter: event.target.value })} required />
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
                  <label htmlFor="sales-date">Fecha de emisión</label>
                  <FormInput id="sales-date" type="date" value={salesForm.issue_date} onChange={(event) => setSalesForm({ ...salesForm, issue_date: event.target.value })} required />
                </FormField>
                <FormField>
                  <label htmlFor="sales-due-date">Fecha estimada de cobro</label>
                  <FormInput id="sales-due-date" type="date" value={salesForm.estimated_payment_date} onChange={(event) => setSalesForm({ ...salesForm, estimated_payment_date: event.target.value })} required />
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
          {!suppliers.length ? (
            <EmptyState>
              Registra un proveedor en <Link to="/companies">Empresas</Link> antes de cargar una compra.
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
                        onChange={(event) => setPurchaseForm({ ...purchaseForm, supplier_id: event.target.value })}
                        required
                      >
                        <option value="">Seleccionar proveedor</option>
                        {suppliers.map((company) => (
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
                      <label htmlFor="purchase-due-date">Vencimiento (opcional)</label>
                      <FormInput id="purchase-due-date" type="date" value={purchaseForm.due_date} onChange={(event) => setPurchaseForm({ ...purchaseForm, due_date: event.target.value })} />
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
                        onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, issuer_id: event.target.value })}
                        required
                      >
                        <option value="">Seleccionar proveedor</option>
                        {suppliers.map((company) => (
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
                      <FormInput id="formal-purchase-letter" value={formalPurchaseForm.letter} maxLength="1" onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, letter: event.target.value.toUpperCase() })} required />
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
                      <FormInput id="formal-purchase-date" type="date" value={formalPurchaseForm.issue_date} onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, issue_date: event.target.value })} required />
                    </FormField>
                    <FormField>
                      <label htmlFor="formal-purchase-due-date">Vencimiento (opcional)</label>
                      <FormInput id="formal-purchase-due-date" type="date" value={formalPurchaseForm.due_date} onChange={(event) => setFormalPurchaseForm({ ...formalPurchaseForm, due_date: event.target.value })} />
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

      <Panel as="section">
        <SectionHeading>
          <h2>{tab === 'sales' ? 'Facturas de venta' : 'Compras y facturas de proveedor'}</h2>
          <span>{isLoading ? 'Cargando…' : `${tab === 'sales' ? salesInvoices.length : purchaseInvoices.length} registros`}</span>
        </SectionHeading>
        {isLoading ? (
          <p role="status">Cargando movimientos…</p>
        ) : tab === 'sales' ? (
          <InvoiceList>
            <StyledTable>
              <thead>
                <tr>
                  <TableHeader>Factura</TableHeader>
                  <TableHeader>Emisor / cliente</TableHeader>
                  <TableHeader>Importe</TableHeader>
                  <TableHeader>Estado</TableHeader>
                  <TableHeader>Acciones</TableHeader>
                </tr>
              </thead>
              <tbody>
                {salesInvoices.map((invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell>{invoice.letra || '—'} {invoice.punto_venta || '—'}-{invoice.nro_factura || '—'}</TableCell>
                    <TableCell>
                      {companyNames.get(invoice.emisor_id) || 'Emisor anterior'} → {companyNames.get(invoice.cliente_id) || 'Cliente'}
                    </TableCell>
                    <TableCell className="numeric">{formatCurrency(invoice.monto_total)}</TableCell>
                    <TableCell><StatusBadge $status={invoice.estado === 'pagado' ? 'saldada' : invoice.estado === 'vencida' ? 'vencida' : 'pendiente'}>{invoice.estado || 'pendiente'}</StatusBadge></TableCell>
                    <TableCell>
                      <ActionCell>
                        <Button type="button" $variant="secondary" onClick={() => toggleSettlement(invoice.id, 'collection')}>
                          Registrar cobro
                        </Button>
                        {settlement?.invoiceId === invoice.id && settlement.type === 'collection' && (
                          <ActionForm onSubmit={(event) => handleSettlement(event, invoice.id, 'collection')}>
                            <FormInput name="amount" type="number" min="0.01" step="0.01" placeholder="Importe" required />
                            <Button type="submit" disabled={isSubmitting}><TbArrowDownLeft /> Cobrar</Button>
                          </ActionForm>
                        )}
                      </ActionCell>
                    </TableCell>
                  </TableRow>
                ))}
              </tbody>
            </StyledTable>
            {!salesInvoices.length && <EmptyState>Aún no hay facturas de venta.</EmptyState>}
          </InvoiceList>
        ) : (
          <InvoiceList>
            <StyledTable>
              <thead>
                <tr>
                  <TableHeader>Registro</TableHeader>
                  <TableHeader>Proveedor / concepto</TableHeader>
                  <TableHeader>Importe</TableHeader>
                  <TableHeader>Estado</TableHeader>
                  <TableHeader>Acciones</TableHeader>
                </tr>
              </thead>
              <tbody>
                {purchaseInvoices.map((invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell>
                      <strong>{invoice.numero_interno || `Compra ${invoice.id}`}</strong>
                      <span>{invoice.factura_recibida ? `Factura ${invoice.letra || ''} ${invoice.punto_venta || ''}-${invoice.nro_factura || ''}` : 'Factura formal pendiente'}</span>
                    </TableCell>
                    <TableCell>
                      {companyNames.get(invoice.proveedor_id) || 'Proveedor'}
                      {invoice.concepto && <span>{invoice.concepto}</span>}
                    </TableCell>
                    <TableCell className="numeric">{formatCurrency(invoice.monto_total)}</TableCell>
                    <TableCell><StatusBadge $status={invoice.estado === 'pagado' ? 'saldada' : invoice.estado === 'vencida' ? 'vencida' : 'pendiente'}>{invoice.estado || 'pendiente'}</StatusBadge></TableCell>
                    <TableCell>
                      <ActionCell>
                        <Button type="button" $variant="secondary" onClick={() => toggleSettlement(invoice.id, 'payment')}>
                          Registrar pago
                        </Button>
                        {!invoice.factura_recibida && (
                          <Button type="button" $variant="secondary" onClick={() => {
                            setFormalizing(formalizing?.id === invoice.id ? null : invoice);
                            setSettlement(null);
                          }}>
                            <TbFileInvoice aria-hidden="true" /> Completar factura
                          </Button>
                        )}
                        {settlement?.invoiceId === invoice.id && settlement.type === 'payment' && (
                          <ActionForm onSubmit={(event) => handleSettlement(event, invoice.id, 'payment')}>
                            <FormInput name="amount" type="number" min="0.01" step="0.01" placeholder="Importe" required />
                            <Button type="submit" disabled={isSubmitting}><TbArrowUpRight /> Pagar</Button>
                          </ActionForm>
                        )}
                        {formalizing?.id === invoice.id && (
                          <ActionForm onSubmit={(event) => handleCompletePurchase(event, invoice.id)}>
                            <FormInput name="letter" maxLength="1" placeholder="Letra" aria-label="Letra" required />
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
            {!purchaseInvoices.length && <EmptyState>Aún no hay compras registradas.</EmptyState>}
          </InvoiceList>
        )}
      </Panel>
    </>
  );
};

export default Invoices;
