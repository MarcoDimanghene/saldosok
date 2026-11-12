const defaultApiUrl = import.meta.env.DEV
  ? 'http://localhost:8000'
  : 'https://saldosok-back.vercel.app';

export const API_URL = (import.meta.env.VITE_API_URL || defaultApiUrl).replace(/\/+$/, '');

export const MAX_USERS_PER_TENANT = 10;

export const CONDICIONES_IVA = [
  'Responsable Inscripto',
  'Monotributo',
  'Exento',
  'Consumidor Final',
];

export const INVOICE_LETTERS = ['A', 'B', 'C', 'E', 'M'];
export const INVOICE_TYPE_LABELS = {
  factura: 'Factura',
  nota_credito: 'Nota de crédito',
  nota_debito: 'Nota de débito',
};
