import { useCallback, useEffect, useState } from 'react';
import { getAuditLogs } from '../../services/auditService';
import {
  AuditContainer,
  AuditDetails,
  AuditFooter,
  AuditHeader,
  AuditMessage,
  AuditPanel,
  AuditTable,
  AuditTableWrap,
  LoadMoreButton,
} from './AuditLog.styles';

const PAGE_SIZE = 100;
const ACTION_LABELS = {
  created: 'Creación',
  updated: 'Edición',
  deleted: 'Eliminación',
  invitation_sent: 'Invitación enviada',
  invitation_resent: 'Invitación reenviada',
  password_set: 'Contraseña configurada',
  password_reset: 'Contraseña restablecida',
};
const ENTITY_LABELS = {
  sales_invoice: 'Factura de venta',
  purchase_invoice: 'Factura de compra',
  sales_collection: 'Cobro',
  purchase_payment: 'Pago',
  user: 'Usuario',
};
const FIELD_LABELS = {
  emisor_id: 'Emisor',
  cliente_id: 'Cliente',
  proveedor_id: 'Proveedor',
  receptor_id: 'Destinatario',
  letra: 'Letra',
  punto_venta: 'Punto de venta',
  nro_factura: 'N.º de factura',
  cae: 'CAE',
  fecha_emision: 'Emisión',
  fecha_pago_approx: 'Cobro estimado',
  fecha_vencimiento: 'Vencimiento',
  monto_total: 'Importe total',
  monto: 'Importe',
  estado: 'Estado',
  invoice_status: 'Estado de factura',
  tipo_comprobante: 'Comprobante',
  factura_origen_id: 'Factura de origen',
  factura_venta_id: 'Factura de venta',
  factura_compra_id: 'Factura de compra',
  metodo_cobro: 'Medio de cobro',
  metodo_pago: 'Medio de pago',
  nro_comprobante: 'N.º de comprobante',
  moneda: 'Moneda',
  factura_recibida: 'Factura recibida',
  concepto: 'Concepto',
  numero_interno: 'N.º interno',
  nombre: 'Nombre',
  username: 'Usuario',
  email: 'Correo',
  is_active: 'Activo',
  is_email_verified: 'Correo confirmado',
  is_tenant_admin: 'Administrador',
  expires_at: 'Vence',
  password_changed: 'Contraseña cambiada',
  method: 'Método',
};

const formatValue = (value) => {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'boolean') return value ? 'Sí' : 'No';
  return String(value);
};

const changesFor = (entry) => {
  const before = entry.before_data || {};
  const after = entry.after_data || {};
  const fields = new Set([...Object.keys(before), ...Object.keys(after)]);

  return [...fields]
    .filter((field) => JSON.stringify(before[field]) !== JSON.stringify(after[field]))
    .map((field) => {
      const label = FIELD_LABELS[field] || field;
      if (before[field] === undefined) return `${label}: ${formatValue(after[field])}`;
      if (after[field] === undefined) return `${label}: ${formatValue(before[field])} (eliminado)`;
      return `${label}: ${formatValue(before[field])} → ${formatValue(after[field])}`;
    });
};

const formatTimestamp = (value) => new Intl.DateTimeFormat('es-AR', {
  dateStyle: 'short',
  timeStyle: 'short',
}).format(new Date(value));

const AuditLog = () => {
  const [entries, setEntries] = useState([]);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadEntries = useCallback(async (offset = 0, append = false) => {
    setIsLoading(true);
    setError(null);
    try {
      const page = await getAuditLogs({ skip: offset, limit: PAGE_SIZE });
      setEntries((current) => (append ? [...current, ...page] : page));
      setSkip(offset + page.length);
      setHasMore(page.length === PAGE_SIZE);
    } catch (loadError) {
      setError(loadError.message || 'No se pudo cargar la auditoría.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    getAuditLogs({ skip: 0, limit: PAGE_SIZE })
      .then((page) => {
        if (!isMounted) return;
        setEntries(page);
        setSkip(page.length);
        setHasMore(page.length === PAGE_SIZE);
      })
      .catch((loadError) => {
        if (isMounted) setError(loadError.message || 'No se pudo cargar la auditoría.');
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <AuditContainer>
      <AuditHeader>
        <h1>Auditoría</h1>
        <p>Historial de cambios en facturas, cobros, pagos y usuarios.</p>
      </AuditHeader>

      <AuditPanel>
        {error && <AuditMessage $error role="alert">{error}</AuditMessage>}
        {!error && entries.length === 0 && !isLoading && (
          <AuditMessage>No hay cambios registrados todavía.</AuditMessage>
        )}
        {entries.length > 0 && (
          <AuditTableWrap>
            <AuditTable>
              <thead>
                <tr>
                  <th scope="col">Fecha</th>
                  <th scope="col">Usuario</th>
                  <th scope="col">Acción</th>
                  <th scope="col">Elemento</th>
                  <th scope="col">Cambios</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => {
                  const changes = changesFor(entry);
                  return (
                    <tr key={entry.id}>
                      <td>{formatTimestamp(entry.created_at)}</td>
                      <td>{entry.actor_name || 'Usuario eliminado'}</td>
                      <td>{ACTION_LABELS[entry.action] || entry.action}</td>
                      <td>
                        {ENTITY_LABELS[entry.entity_type] || entry.entity_type}
                        {entry.entity_id ? ` #${entry.entity_id}` : ''}
                      </td>
                      <td>
                        {changes.length ? (
                          <AuditDetails>
                            {changes.map((change) => <li key={change}>{change}</li>)}
                          </AuditDetails>
                        ) : '—'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </AuditTable>
          </AuditTableWrap>
        )}

        <AuditFooter>
          <AuditMessage role="status">
            {isLoading ? 'Cargando cambios…' : `${entries.length} cambios cargados`}
          </AuditMessage>
          {hasMore && (
            <LoadMoreButton
              type="button"
              onClick={() => loadEntries(skip, true)}
              disabled={isLoading}
            >
              {isLoading ? 'Cargando…' : 'Cargar más'}
            </LoadMoreButton>
          )}
        </AuditFooter>
      </AuditPanel>
    </AuditContainer>
  );
};

export default AuditLog;
