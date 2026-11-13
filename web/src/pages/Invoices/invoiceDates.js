function parseDate(dateValue) {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(dateValue || ''));
  if (!match) return null;

  const [, year, month, day] = match;
  return Date.UTC(Number(year), Number(month) - 1, Number(day));
}

export function companyTermDays(company, field) {
  const days = Number(company?.[field] ?? company?.dias_credito ?? 0);
  return Number.isInteger(days) && days >= 0 ? days : 0;
}

export function addDaysToDate(dateValue, daysValue) {
  const timestamp = parseDate(dateValue);
  if (timestamp === null || daysValue === '' || daysValue === null) return '';

  const days = Number(daysValue);
  if (!Number.isInteger(days) || days < 0) return '';

  return new Date(timestamp + days * 86_400_000).toISOString().slice(0, 10);
}

export function daysUntil(dateValue, referenceDate = new Date()) {
  const target = parseDate(dateValue);
  if (target === null) return null;

  const reference = typeof referenceDate === 'string'
    ? parseDate(referenceDate)
    : Date.UTC(
      referenceDate.getFullYear(),
      referenceDate.getMonth(),
      referenceDate.getDate(),
    );
  if (reference === null) return null;

  return Math.round((target - reference) / 86_400_000);
}

export function formatInvoiceDate(dateValue) {
  const timestamp = parseDate(dateValue);
  if (timestamp === null) return null;

  return new Intl.DateTimeFormat('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(timestamp);
}

export function formatDateCountdown(dateValue, type, referenceDate = new Date()) {
  const days = daysUntil(dateValue, referenceDate);
  if (days === null) return null;
  const dayUnit = Math.abs(days) === 1 ? 'día' : 'días';

  if (type === 'collection') {
    if (days === 0) return 'Cobro estimado hoy';
    if (days > 0) return `Cobro estimado en ${days} ${dayUnit}`;
    return `Fecha estimada hace ${Math.abs(days)} ${dayUnit}`;
  }

  if (days === 0) return 'Vence hoy';
  if (days > 0) return `Vence en ${days} ${dayUnit}`;
  return `Vencida hace ${Math.abs(days)} ${dayUnit}`;
}
