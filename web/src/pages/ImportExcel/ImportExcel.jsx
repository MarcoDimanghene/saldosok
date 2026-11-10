import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
import { TbDownload, TbFileSpreadsheet, TbUpload } from 'react-icons/tb';
import { Button } from '../../component/ui/UIComponents';
import { fetchDashboard, fetchPurchaseInvoices, fetchSalesInvoices } from '../../store';
import { importFinance } from '../../services/financeImportService';
import {
  downloadFinanceTemplate,
  readFinanceWorkbook,
} from './excelTemplate';
import {
  ActionRow,
  ErrorList,
  FileInput,
  Guidance,
  PageHeader,
  Panel,
  StatusMessage,
} from './ImportExcel.styles';

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const EMPTY_COUNTS = { sales: 0, purchases: 0, collections: 0, payments: 0 };

const ImportExcel = () => {
  const dispatch = useDispatch();
  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0] || null;
    setFile(selectedFile);
    setError(null);
    setResult(null);
    if (!selectedFile) return;
    if (!selectedFile.name.toLowerCase().endsWith('.xlsx')) {
      setError('Seleccioná un archivo de Excel con formato .xlsx.');
    } else if (selectedFile.size > MAX_FILE_SIZE) {
      setError('El archivo supera el límite de 5 MB.');
    }
  };

  const handleDownloadTemplate = async () => {
    setError(null);
    try {
      await downloadFinanceTemplate();
    } catch (downloadError) {
      setError(downloadError.message || 'No se pudo generar la plantilla Excel.');
    }
  };

  const handleImport = async (event) => {
    event.preventDefault();
    if (!file || error) return;

    setIsSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const rows = await readFinanceWorkbook(file);
      const rowCount = Object.values(rows).reduce((total, items) => total + items.length, 0);
      if (!rowCount) {
        setError('La planilla no contiene filas para importar.');
        return;
      }

      const response = await importFinance(rows);
      if (!response.ok) {
        setResult({ errors: response.errors || [] });
        return;
      }

      setResult({ imported: { ...EMPTY_COUNTS, ...response.imported } });
      await Promise.all([
        dispatch(fetchDashboard({ force: true })),
        dispatch(fetchSalesInvoices({ force: true })),
        dispatch(fetchPurchaseInvoices({ force: true })),
      ]);
    } catch (requestError) {
      setError(requestError.message || 'No se pudo procesar la planilla.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const imported = result?.imported;

  return (
    <>
      <PageHeader>
        <h1>Importar desde Excel</h1>
        <p>Migrá facturas de venta y compra, junto con sus cobros y pagos, en una sola operación.</p>
      </PageHeader>

      <Panel as="section">
        <h2>1. Descargá y completá la plantilla</h2>
        <Guidance>
          <li>La plantilla contiene hojas independientes para Ventas, Compras, Cobros y Pagos.</li>
          <li>Los CUIT deben pertenecer a empresas ya registradas con el rol adecuado en <Link to="/companies">Empresas</Link>.</li>
          <li>Las compras de esta plantilla corresponden a facturas formales; los pagos y cobros se vinculan por los datos de la factura.</li>
          <li>Se aceptan facturas nuevas incluidas en el archivo y movimientos aplicados a facturas ya existentes.</li>
          <li>La importación es integral: ante cualquier error no se guarda ninguna fila. Corregí los errores informados y volvé a importar.</li>
        </Guidance>
        <Button type="button" $variant="secondary" onClick={handleDownloadTemplate}>
          <TbDownload aria-hidden="true" /> Descargar plantilla Excel
        </Button>
      </Panel>

      <Panel as="section">
        <h2>2. Seleccioná la planilla completa</h2>
        <form onSubmit={handleImport}>
          <FileInput
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            aria-label="Seleccionar planilla de Excel"
            onChange={handleFileChange}
          />
          <ActionRow>
            <Button type="submit" disabled={!file || Boolean(error) || isSubmitting}>
              <TbUpload aria-hidden="true" />
              {isSubmitting ? 'Validando e importando…' : 'Validar e importar'}
            </Button>
            {file && <span>{file.name}</span>}
          </ActionRow>
        </form>

        {error && <StatusMessage $error role="alert">{error}</StatusMessage>}
        {result?.errors && (
          <StatusMessage $error role="alert">
            <strong>No se importó ningún dato. Corregí estas filas y volvé a intentarlo:</strong>
            <ErrorList>
              {result.errors.map((item, index) => (
                <li key={`${item.sheet}-${item.row}-${item.field}-${index}`}>
                  {item.sheet}{item.row ? `, fila ${item.row}` : ''}
                  {item.field ? `, ${item.field}` : ''}: {item.message}
                </li>
              ))}
            </ErrorList>
          </StatusMessage>
        )}
        {imported && (
          <StatusMessage role="status">
            <strong>Importación completada.</strong>
            <ul>
              <li>Ventas: {imported.sales}</li>
              <li>Compras: {imported.purchases}</li>
              <li>Cobros: {imported.collections}</li>
              <li>Pagos: {imported.payments}</li>
            </ul>
          </StatusMessage>
        )}
        {isSubmitting && (
          <p role="status">
            <TbFileSpreadsheet aria-hidden="true" /> Revisando la planilla. No cierres esta página.
          </p>
        )}
      </Panel>
    </>
  );
};

export default ImportExcel;
