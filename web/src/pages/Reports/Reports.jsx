import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Button } from '../../component/ui/UIComponents';
import { fetchDashboard, fetchPurchaseInvoices } from '../../store';
import {
  ReportCard,
  ReportGrid,
  ReportMessage,
  ReportRows,
  ReportSection,
  ReportsContainer,
  ReportsHeader,
} from './Reports.styles';

const currency = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 2,
});
const formatCurrency = (amount) => currency.format(Number(amount) || 0);

const Reports = () => {
  const dispatch = useDispatch();
  const { summary, status, error } = useSelector((state) => state.dashboard);
  const { purchases, purchasesStatus, purchasesError } = useSelector((state) => state.invoices);
  const loading = ['idle', 'loading'].includes(status)
    || ['idle', 'loading'].includes(purchasesStatus);

  useEffect(() => {
    dispatch(fetchDashboard());
    dispatch(fetchPurchaseInvoices());
  }, [dispatch]);

  const missingInvoices = purchases.filter((purchase) => !purchase.factura_recibida).length;

  return (
    <ReportsContainer>
      <ReportsHeader>
        <h1>Informes</h1>
        <p>Resumen de ventas, compras, saldos y documentación pendiente.</p>
      </ReportsHeader>

      {loading && <ReportMessage role="status">Cargando informes…</ReportMessage>}
      {!loading && (error || purchasesError) && (
        <ReportMessage $error role="alert">{error || purchasesError}</ReportMessage>
      )}
      {!loading && !error && !purchasesError && summary && (
        <>
          <ReportGrid>
            <ReportCard>
              <h2>Ventas acumuladas</h2>
              <strong>{formatCurrency(summary.total_sales)}</strong>
            </ReportCard>
            <ReportCard>
              <h2>Compras acumuladas</h2>
              <strong>{formatCurrency(summary.total_purchases)}</strong>
            </ReportCard>
            <ReportCard>
              <h2>Saldo (ventas − compras)</h2>
              <strong>{formatCurrency(summary.balance)}</strong>
            </ReportCard>
            <ReportCard>
              <h2>Facturas de compra pendientes</h2>
              <strong>{missingInvoices}</strong>
            </ReportCard>
          </ReportGrid>

          <ReportGrid>
            <ReportSection as="section">
              <h2>Ventas por estado</h2>
              {summary.sales_by_status.length ? (
                <ReportRows>
                  {summary.sales_by_status.map((item) => (
                    <li key={item.estado}>
                      <span>{item.estado} · {item.cantidad}</span>
                      <span>{formatCurrency(item.monto)}</span>
                    </li>
                  ))}
                </ReportRows>
              ) : <ReportMessage>No hay ventas registradas.</ReportMessage>}
            </ReportSection>
            <ReportSection as="section">
              <h2>Compras por estado</h2>
              {summary.purchases_by_status.length ? (
                <ReportRows>
                  {summary.purchases_by_status.map((item) => (
                    <li key={item.estado}>
                      <span>{item.estado} · {item.cantidad}</span>
                      <span>{formatCurrency(item.monto)}</span>
                    </li>
                  ))}
                </ReportRows>
              ) : <ReportMessage>No hay compras registradas.</ReportMessage>}
            </ReportSection>
          </ReportGrid>

          <ReportGrid>
            <ReportSection as="section">
              <h2>Principales clientes</h2>
              {summary.top_clients.length ? (
                <ReportRows>
                  {summary.top_clients.map((client) => (
                    <li key={client.company_id}>
                      <span>{client.razon_social}</span>
                      <span>{formatCurrency(client.monto)}</span>
                    </li>
                  ))}
                </ReportRows>
              ) : <ReportMessage>No hay ventas para informar.</ReportMessage>}
            </ReportSection>
            <ReportSection as="section">
              <h2>Principales proveedores</h2>
              {summary.top_suppliers.length ? (
                <ReportRows>
                  {summary.top_suppliers.map((supplier) => (
                    <li key={supplier.company_id}>
                      <span>{supplier.razon_social}</span>
                      <span>{formatCurrency(supplier.monto)}</span>
                    </li>
                  ))}
                </ReportRows>
              ) : <ReportMessage>No hay compras para informar.</ReportMessage>}
            </ReportSection>
          </ReportGrid>

          <ReportCard as="section">
            <h2>Vencimientos atrasados</h2>
            <ReportRows>
              <li>
                <span>Cobros pendientes · {summary.overdue_sales_count}</span>
                <span>{formatCurrency(summary.overdue_sales_amount)}</span>
              </li>
              <li>
                <span>Pagos pendientes · {summary.overdue_purchases_count}</span>
                <span>{formatCurrency(summary.overdue_purchases_amount)}</span>
              </li>
            </ReportRows>
            <Button as={Link} to="/invoices" $variant="secondary" style={{ marginTop: '1rem' }}>
              Ver ventas y compras
            </Button>
          </ReportCard>
        </>
      )}
    </ReportsContainer>
  );
};

export default Reports;
