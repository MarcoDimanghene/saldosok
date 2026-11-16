import { useCallback, useEffect, useMemo, useState } from 'react';
import { TbChartLine, TbPlus } from 'react-icons/tb';
import { Button, StyledTable, TableCell, TableHeader, TableRow } from '../../component/ui/UIComponents';
import {
  createOperatingResult,
  getOperatingResults,
  updateOperatingResult,
} from '../../services/invoiceService';
import {
  Form,
  FormField,
  FormInput,
  Message,
  PageContainer,
  PageHeader,
  Panel,
  Preview,
  TableWrap,
} from './OperatingResults.styles';

const invoiceLabel = (invoice) => (
  invoice.letra && invoice.punto_venta != null && invoice.nro_factura != null
    ? `${invoice.letra} ${invoice.punto_venta}-${invoice.nro_factura}`
    : invoice.numero_interno || `#${invoice.factura_compra_id}`
);

const formatCurrency = (amount, currency = 'ARS') => {
  try {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: currency || 'ARS',
      maximumFractionDigits: 2,
    }).format(Number(amount) || 0);
  } catch {
    return `${Number(amount || 0).toLocaleString('es-AR', { maximumFractionDigits: 2 })} ${currency}`;
  }
};

const formatDate = (date) => (
  date ? new Date(`${date}T00:00:00`).toLocaleDateString('es-AR') : '—'
);

const OperatingResults = () => {
  const [results, setResults] = useState([]);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [saleAmount, setSaleAmount] = useState('');
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const loadResults = useCallback(async () => {
    setStatus('loading');
    setError('');
    try {
      setResults(await getOperatingResults());
      setStatus('ready');
    } catch (loadError) {
      setError(loadError.message);
      setStatus('error');
    }
  }, []);

  useEffect(() => {
    let isCurrent = true;
    getOperatingResults()
      .then((items) => {
        if (!isCurrent) return;
        setResults(items);
        setStatus('ready');
      })
      .catch((loadError) => {
        if (!isCurrent) return;
        setError(loadError.message);
        setStatus('error');
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const preview = useMemo(() => {
    if (!selectedInvoice || saleAmount === '') return null;
    const sale = Number(saleAmount);
    if (!Number.isFinite(sale) || sale <= 0) return null;
    const profit = sale - Number(selectedInvoice.monto_compra || 0);
    return {
      profit,
      percentage: (profit / sale) * 100,
    };
  }, [saleAmount, selectedInvoice]);

  const openEditor = (invoice) => {
    setSelectedInvoice(invoice);
    setSaleAmount(invoice.monto_venta ?? '');
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedInvoice) return;

    setIsSaving(true);
    setError('');
    try {
      const payload = { monto_venta: saleAmount };
      if (selectedInvoice.id) {
        await updateOperatingResult(selectedInvoice.id, payload);
      } else {
        await createOperatingResult({
          ...payload,
          factura_compra_id: selectedInvoice.factura_compra_id,
        });
      }
      setSelectedInvoice(null);
      setSaleAmount('');
      await loadResults();
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <PageContainer>
      <PageHeader>
        <div>
          <h1>Resultado Operativo</h1>
          <p>Registrá el valor de venta de cada factura y consultá la ganancia calculada.</p>
        </div>
      </PageHeader>

      {selectedInvoice && (
        <Panel>
          <h2>{selectedInvoice.id ? 'Editar Resultado Operativo' : 'Agregar Resultado Operativo'}</h2>
          <Message>
            Factura {invoiceLabel(selectedInvoice)} · {selectedInvoice.proveedor} ·
            {' '}Costo: {formatCurrency(selectedInvoice.monto_compra, selectedInvoice.moneda)}
          </Message>
          <Form onSubmit={handleSubmit}>
            <FormField>
              Valor de venta ({selectedInvoice.moneda || 'ARS'})
              <FormInput
                autoFocus
                required
                min="0.01"
                step="0.01"
                type="number"
                value={saleAmount}
                onChange={(event) => setSaleAmount(event.target.value)}
              />
            </FormField>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? 'Guardando…' : 'Guardar RO'}
            </Button>
            {preview && (
              <Preview>
                Ganancia: <strong>{formatCurrency(preview.profit, selectedInvoice.moneda)}</strong>
                {' · '}Porcentaje sobre venta: <strong>{preview.percentage.toFixed(2)}%</strong>
              </Preview>
            )}
          </Form>
          {error && <Message $error role="alert">{error}</Message>}
          <Button
            type="button"
            $variant="ghost"
            onClick={() => setSelectedInvoice(null)}
            style={{ marginTop: '0.75rem' }}
          >
            Cancelar
          </Button>
        </Panel>
      )}

      {!selectedInvoice && error && <Message $error role="alert">{error}</Message>}
      {status === 'loading' && <Message role="status">Cargando facturas…</Message>}
      {status === 'ready' && (
        <Panel>
          <TableWrap>
            <StyledTable>
              <thead>
                <tr>
                  <TableHeader>Factura</TableHeader>
                  <TableHeader>Proveedor</TableHeader>
                  <TableHeader>Fecha</TableHeader>
                  <TableHeader>Costo</TableHeader>
                  <TableHeader>Venta</TableHeader>
                  <TableHeader>Ganancia</TableHeader>
                  <TableHeader>% sobre venta</TableHeader>
                  <TableHeader>Acción</TableHeader>
                </tr>
              </thead>
              <tbody>
                {results.map((invoice) => (
                  <TableRow key={invoice.factura_compra_id}>
                    <TableCell>{invoiceLabel(invoice)}</TableCell>
                    <TableCell>{invoice.proveedor}</TableCell>
                    <TableCell>{formatDate(invoice.fecha_emision)}</TableCell>
                    <TableCell className="numeric">
                      {formatCurrency(invoice.monto_compra, invoice.moneda)}
                    </TableCell>
                    <TableCell className="numeric">
                      {invoice.monto_venta == null
                        ? '—'
                        : formatCurrency(invoice.monto_venta, invoice.moneda)}
                    </TableCell>
                    <TableCell className="numeric">
                      {invoice.ganancia == null
                        ? '—'
                        : formatCurrency(invoice.ganancia, invoice.moneda)}
                    </TableCell>
                    <TableCell className="numeric">
                      {invoice.porcentaje_venta == null ? '—' : `${invoice.porcentaje_venta}%`}
                    </TableCell>
                    <TableCell>
                      <Button
                        type="button"
                        $variant={invoice.id ? 'secondary' : 'primary'}
                        onClick={() => openEditor(invoice)}
                      >
                        {invoice.id ? <TbChartLine aria-hidden="true" /> : <TbPlus aria-hidden="true" />}
                        {invoice.id ? 'Editar RO' : 'Agregar RO'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </tbody>
            </StyledTable>
          </TableWrap>
          {!results.length && (
            <Message>No hay facturas formales de compra para mostrar.</Message>
          )}
        </Panel>
      )}
    </PageContainer>
  );
};

export default OperatingResults;
