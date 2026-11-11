import { useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  TbArrowDownRight,
  TbArrowUpRight,
  TbChartBar,
  TbRefresh,
  TbWallet,
} from 'react-icons/tb';
import { useAuth } from '../../hook/useAuth';
import { fetchDashboard } from '../../store';
import { Button } from '../../component/ui/UIComponents';
import {
  DashboardCard,
  DashboardContainer,
  DashboardHeader,
  DashboardSubtitle,
  DashboardTitle,
  EmptyState,
  ErrorMessage,
  HeaderActions,
  LoadingState,
  MetricCard,
  MetricIcon,
  MetricLabel,
  MetricValue,
  PartnerAmount,
  PartnerList,
  PartnerRow,
  ProgressTrack,
  SectionHeading,
  SectionTitle,
  SummaryGrid,
  TwoColumnGrid,
  UpcomingGrid,
  UpcomingItem,
} from './Dashboard.styles';

const currencyFormatter = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 0,
});

const formatCurrency = (value) => {
  const amount = Number(value);
  return currencyFormatter.format(Number.isFinite(amount) ? amount : 0);
};

const formatPercentage = (value) => (
  value == null ? 'Sin datos' : `${Number(value).toLocaleString('es-AR')}%`
);

const Dashboard = () => {
  const { user, tenant } = useAuth();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { summary, status, error } = useSelector((state) => state.dashboard);
  const loading = status === 'idle' || status === 'loading';

  const loadSummary = useCallback(async () => {
    await dispatch(fetchDashboard({ force: true }));
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchDashboard());
  }, [dispatch]);

  const chartData = summary ? [
    {
      periodo: 'Mes anterior',
      ventas: Number(summary.sales_prev_month) || 0,
      compras: Number(summary.purchases_prev_month) || 0,
    },
    {
      periodo: 'Este mes',
      ventas: Number(summary.sales_this_month) || 0,
      compras: Number(summary.purchases_this_month) || 0,
    },
  ] : [];

  const renderPartners = (partners) => (
    partners?.length ? (
      <PartnerList>
        {partners.map((partner) => (
          <PartnerRow key={partner.company_id}>
            <span>{partner.razon_social}</span>
            <PartnerAmount>{formatCurrency(partner.monto)}</PartnerAmount>
          </PartnerRow>
        ))}
      </PartnerList>
    ) : (
      <EmptyState>Todavía no hay movimientos para mostrar.</EmptyState>
    )
  );

  return (
    <DashboardContainer>
      <DashboardHeader>
        <div>
          <DashboardTitle>Hola, {user?.nombre || user?.username}</DashboardTitle>
          <DashboardSubtitle>
            Este es el resumen financiero de {tenant?.razon_social || 'tu espacio de trabajo'}.
          </DashboardSubtitle>
        </div>
        <HeaderActions>
          {user?.is_tenant_admin && (
            <Button type="button" onClick={() => navigate('/users')}>
              Gestionar usuarios
            </Button>
          )}
        </HeaderActions>
      </DashboardHeader>

      {loading && (
        <LoadingState role="status" aria-live="polite">
          Cargando el resumen financiero…
        </LoadingState>
      )}

      {!loading && error && (
        <ErrorMessage role="alert">
          <span>{error}</span>
          <Button type="button" $variant="secondary" onClick={loadSummary}>
            <TbRefresh aria-hidden="true" /> Reintentar
          </Button>
        </ErrorMessage>
      )}

      {!loading && !error && summary && (
        <>
          <SummaryGrid>
            <MetricCard>
              <MetricIcon><TbWallet /></MetricIcon>
              <MetricLabel>Cuentas por cobrar</MetricLabel>
              <MetricValue>{formatCurrency(summary.accounts_receivable)}</MetricValue>
              <span>Cobrado: {formatPercentage(summary.collection_rate)}</span>
            </MetricCard>
            <MetricCard>
              <MetricIcon $tone="warning"><TbArrowDownRight /></MetricIcon>
              <MetricLabel>Cuentas por pagar</MetricLabel>
              <MetricValue>{formatCurrency(summary.accounts_payable)}</MetricValue>
              <span>Pagado: {formatPercentage(summary.payment_rate)}</span>
            </MetricCard>
            <MetricCard>
              <MetricIcon><TbArrowUpRight /></MetricIcon>
              <MetricLabel>Ventas acumuladas</MetricLabel>
              <MetricValue>{formatCurrency(summary.total_sales)}</MetricValue>
              <span>Este mes: {formatCurrency(summary.sales_this_month)}</span>
            </MetricCard>
            <MetricCard>
              <MetricIcon $tone="muted"><TbChartBar /></MetricIcon>
              <MetricLabel>Compras acumuladas</MetricLabel>
              <MetricValue>{formatCurrency(summary.total_purchases)}</MetricValue>
              <span>Este mes: {formatCurrency(summary.purchases_this_month)}</span>
            </MetricCard>
          </SummaryGrid>

          {(summary.overdue_sales_count > 0 || summary.overdue_purchases_count > 0) && (
            <ErrorMessage role="status">
              <strong>Hay vencimientos pendientes:</strong>
              <span>
                {summary.overdue_sales_count > 0
                  && ` ${summary.overdue_sales_count} cobro(s) por ${formatCurrency(summary.overdue_sales_amount)}.`}
                {summary.overdue_purchases_count > 0
                  && ` ${summary.overdue_purchases_count} pago(s) por ${formatCurrency(summary.overdue_purchases_amount)}.`}
              </span>
            </ErrorMessage>
          )}

          <DashboardCard as="section">
            <SectionHeading>
              <SectionTitle>Pronóstico de cobranzas</SectionTitle>
              <span>Saldo pendiente según fecha estimada de cobro</span>
            </SectionHeading>
            <SummaryGrid>
              <MetricCard>
                <MetricIcon><TbWallet /></MetricIcon>
                <MetricLabel>Esta semana</MetricLabel>
                <MetricValue>{formatCurrency(summary.collections_this_week)}</MetricValue>
              </MetricCard>
              <MetricCard>
                <MetricIcon><TbWallet /></MetricIcon>
                <MetricLabel>La próxima semana</MetricLabel>
                <MetricValue>{formatCurrency(summary.collections_next_week)}</MetricValue>
              </MetricCard>
              <MetricCard>
                <MetricIcon><TbWallet /></MetricIcon>
                <MetricLabel>Este mes</MetricLabel>
                <MetricValue>{formatCurrency(summary.collections_this_month)}</MetricValue>
              </MetricCard>
              <MetricCard>
                <MetricIcon><TbWallet /></MetricIcon>
                <MetricLabel>El próximo mes</MetricLabel>
                <MetricValue>{formatCurrency(summary.collections_next_month)}</MetricValue>
              </MetricCard>
            </SummaryGrid>
          </DashboardCard>

          <TwoColumnGrid>
            <DashboardCard as="section">
              <SectionHeading>
                <SectionTitle>Ventas y compras</SectionTitle>
                <span>Comparación mensual</span>
              </SectionHeading>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={chartData} margin={{ top: 12, right: 8, left: 8, bottom: 4 }}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                  <XAxis dataKey="periodo" tick={{ fill: '#bbc9cd', fontSize: 12 }} />
                  <YAxis
                    tick={{ fill: '#859397', fontSize: 11 }}
                    tickFormatter={(value) => currencyFormatter.format(value)}
                    width={90}
                  />
                  <Tooltip
                    formatter={(value) => formatCurrency(value)}
                    contentStyle={{
                      background: '#131b2e',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '8px',
                      color: '#dae2fd',
                    }}
                  />
                  <Bar dataKey="ventas" name="Ventas" fill="#2fd9f4" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="compras" name="Compras" fill="#a4d64c" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </DashboardCard>

            <DashboardCard as="section">
              <SectionHeading>
                <SectionTitle>Estado de cuentas</SectionTitle>
                <span>Acumulado histórico</span>
              </SectionHeading>
              <div>
                <PartnerRow>
                  <span>Resultado (ventas − compras)</span>
                  <PartnerAmount>{formatCurrency(summary.balance)}</PartnerAmount>
                </PartnerRow>
                <PartnerRow>
                  <span>Total cobrado</span>
                  <PartnerAmount>{formatCurrency(summary.total_collected)}</PartnerAmount>
                </PartnerRow>
                <ProgressTrack
                  role="progressbar"
                  aria-label="Porcentaje de ventas cobradas"
                  aria-valuenow={summary.collection_rate ?? 0}
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
                  <span style={{ width: `${Math.min(Math.max(summary.collection_rate || 0, 0), 100)}%` }} />
                </ProgressTrack>
                <PartnerRow>
                  <span>Total pagado</span>
                  <PartnerAmount>{formatCurrency(summary.total_paid)}</PartnerAmount>
                </PartnerRow>
                <ProgressTrack
                  role="progressbar"
                  aria-label="Porcentaje de compras pagadas"
                  aria-valuenow={summary.payment_rate ?? 0}
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
                  <span style={{ width: `${Math.min(Math.max(summary.payment_rate || 0, 0), 100)}%` }} />
                </ProgressTrack>
              </div>
            </DashboardCard>
          </TwoColumnGrid>

          <DashboardCard as="section">
            <SectionHeading>
              <SectionTitle>Próximos vencimientos</SectionTitle>
              <span>Cobros y pagos pendientes</span>
            </SectionHeading>
            <UpcomingGrid>
              {[7, 15, 30].map((days) => {
                const collections = summary.upcoming_collections.find((item) => item.dias === days);
                const payments = summary.upcoming_payments.find((item) => item.dias === days);

                return (
                  <UpcomingItem key={days}>
                    <strong>Próximos {days} días</strong>
                    <span>
                      Por cobrar · {collections?.cantidad || 0} · {formatCurrency(collections?.monto || 0)}
                    </span>
                    <span>
                      Por pagar · {payments?.cantidad || 0} · {formatCurrency(payments?.monto || 0)}
                    </span>
                  </UpcomingItem>
                );
              })}
            </UpcomingGrid>
          </DashboardCard>

          <TwoColumnGrid>
            <DashboardCard as="section">
              <SectionHeading>
                <SectionTitle>Principales clientes</SectionTitle>
                <span>Por monto vendido</span>
              </SectionHeading>
              {renderPartners(summary.top_clients)}
            </DashboardCard>
            <DashboardCard as="section">
              <SectionHeading>
                <SectionTitle>Principales proveedores</SectionTitle>
                <span>Por monto comprado</span>
              </SectionHeading>
              {renderPartners(summary.top_suppliers)}
            </DashboardCard>
          </TwoColumnGrid>
        </>
      )}
    </DashboardContainer>
  );
};

export default Dashboard;
