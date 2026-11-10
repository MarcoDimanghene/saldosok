import { useCallback, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { TbBuilding, TbBuildingStore, TbDeviceFloppy, TbEdit, TbPlus, TbX } from 'react-icons/tb';
import { Button } from '../../component/ui/UIComponents';
import { createCompany, updateCompany } from '../../services/companyService';
import { fetchCompanies } from '../../store';
import {
  CompanyGrid,
  CompanyItem,
  CompanyList,
  CompanyName,
  CompanyRoles,
  Form,
  FormField,
  FormInput,
  PageHeader,
  Panel,
  RoleChoice,
  StatusMessage,
} from './Companies.styles';

const initialForm = {
  tax_id: '',
  legal_name: '',
  tax_condition: '',
  address: '',
  localidad: '',
  provincia: '',
  is_client: false,
  is_supplier: false,
};

const Companies = () => {
  const dispatch = useDispatch();
  const { items: companies, status, error } = useSelector((state) => state.companies);
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState(null);
  const [editingCompanyId, setEditingCompanyId] = useState(null);
  const portfolioCompanies = companies.filter((company) => !company.es_emisor);

  const loadCompanies = useCallback(async () => {
    await dispatch(fetchCompanies({ force: true }));
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchCompanies());
  }, [dispatch]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage(null);

    const taxId = form.tax_id.replace(/\D/g, '');
    const taxIdRequired = !form.is_supplier || form.is_client;
    if ((taxIdRequired && !taxId) || (taxId && taxId.length !== 11)) {
      setMessage({ error: true, text: 'El CUIT/CUIL debe tener 11 dígitos, excepto para proveedores sin identificación.' });
      return;
    }
    if (!form.is_client && !form.is_supplier) {
      setMessage({ error: true, text: 'Selecciona al menos un rol para esta empresa.' });
      return;
    }

    setIsSubmitting(true);
    try {
      const companyData = {
        ...form,
        legal_name: form.legal_name.trim(),
        tax_condition: form.tax_condition.trim() || null,
        address: form.address.trim() || null,
        localidad: form.localidad.trim() || null,
        provincia: form.provincia.trim() || null,
        tax_id: taxId || null,
      };
      if (editingCompanyId) {
        await updateCompany(editingCompanyId, companyData);
      } else {
        await createCompany(companyData);
      }
      setForm(initialForm);
      setEditingCompanyId(null);
      setMessage({
        error: false,
        text: editingCompanyId ? 'La empresa se actualizó correctamente.' : 'La empresa se registró correctamente.',
      });
      await loadCompanies();
    } catch (error) {
      setMessage({
        error: true,
        text: error.message || (
          editingCompanyId ? 'No se pudo actualizar la empresa.' : 'No se pudo registrar la empresa.'
        ),
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const startEditing = (company) => {
    setEditingCompanyId(company.id);
    setForm({
      tax_id: company.cuit || '',
      legal_name: company.razon_social || '',
      tax_condition: company.condicion_iva || '',
      address: company.domicilio || '',
      localidad: company.localidad || '',
      provincia: company.provincia || '',
      is_client: company.es_cliente,
      is_supplier: company.es_proveedor,
    });
    setMessage(null);
  };

  const cancelEditing = () => {
    setEditingCompanyId(null);
    setForm(initialForm);
    setMessage(null);
  };

  return (
    <>
      <PageHeader>
        <h1>Empresas</h1>
        <p>Administra tu cartera de clientes y proveedores. El emisor se configura en el perfil de organización.</p>
      </PageHeader>

      {message && (
        <StatusMessage $error={message.error} role={message.error ? 'alert' : 'status'}>
          {message.text}
        </StatusMessage>
      )}
      {error && <StatusMessage $error role="alert">{error}</StatusMessage>}

      <CompanyGrid>
        <Panel as="section">
          <h2>{editingCompanyId ? 'Editar empresa' : 'Agregar empresa'}</h2>
          <Form onSubmit={handleSubmit}>
            <FormField>
              <label htmlFor="company-legal-name">Razón social</label>
              <FormInput
                id="company-legal-name"
                value={form.legal_name}
                onChange={(event) => setForm({ ...form, legal_name: event.target.value })}
                autoComplete="organization"
                required
              />
            </FormField>
            <FormField>
              <label htmlFor="company-tax-id">
                CUIT/CUIL{form.is_supplier && !form.is_client ? ' (opcional)' : ''}
              </label>
              <FormInput
                id="company-tax-id"
                inputMode="numeric"
                pattern="[0-9]{11}"
                maxLength="11"
                value={form.tax_id}
                onChange={(event) => setForm({
                  ...form,
                  tax_id: event.target.value.replace(/\D/g, '').slice(0, 11),
                })}
                required={!form.is_supplier || form.is_client}
              />
            </FormField>
            <FormField>
              <label htmlFor="company-tax-condition">Condición de IVA</label>
              <FormInput
                id="company-tax-condition"
                value={form.tax_condition}
                onChange={(event) => setForm({ ...form, tax_condition: event.target.value })}
              />
            </FormField>
            <FormField>
              <label htmlFor="company-address">Domicilio</label>
              <FormInput
                id="company-address"
                value={form.address}
                onChange={(event) => setForm({ ...form, address: event.target.value })}
              />
            </FormField>
            <FormField>
              <label htmlFor="company-locality">Localidad</label>
              <FormInput
                id="company-locality"
                value={form.localidad}
                onChange={(event) => setForm({ ...form, localidad: event.target.value })}
              />
            </FormField>
            <FormField>
              <label htmlFor="company-province">Provincia</label>
              <FormInput
                id="company-province"
                value={form.provincia}
                onChange={(event) => setForm({ ...form, provincia: event.target.value })}
              />
            </FormField>
            <FormField>
              <span>Roles</span>
              <CompanyRoles>
                <RoleChoice>
                  <input
                    type="checkbox"
                    checked={form.is_client}
                    onChange={(event) => setForm({ ...form, is_client: event.target.checked })}
                  />
                  Cliente
                </RoleChoice>
                <RoleChoice>
                  <input
                    type="checkbox"
                    checked={form.is_supplier}
                    onChange={(event) => setForm({ ...form, is_supplier: event.target.checked })}
                  />
                  Proveedor
                </RoleChoice>
              </CompanyRoles>
            </FormField>
            <Button type="submit" disabled={isSubmitting}>
              {editingCompanyId
                ? <TbDeviceFloppy aria-hidden="true" />
                : <TbPlus aria-hidden="true" />}
              {isSubmitting ? 'Guardando…' : editingCompanyId ? 'Guardar cambios' : 'Agregar empresa'}
            </Button>
            {editingCompanyId && (
              <Button type="button" $variant="secondary" onClick={cancelEditing}>
                <TbX aria-hidden="true" /> Cancelar edición
              </Button>
            )}
          </Form>
        </Panel>

        <Panel as="section">
          <h2>Empresas registradas</h2>
          {status === 'idle' || status === 'loading' ? (
            <p role="status">Cargando empresas…</p>
          ) : portfolioCompanies.length ? (
            <CompanyList>
              {portfolioCompanies.map((company) => {
                const roles = [
                  company.es_cliente && 'Cliente',
                  company.es_proveedor && 'Proveedor',
                ].filter(Boolean);

                return (
                  <CompanyItem key={company.id}>
                    <CompanyName>
                      <TbBuilding aria-hidden="true" />
                      <div>
                        <strong>{company.razon_social}</strong>
                        <span>
                          {company.cuit ? `CUIT/CUIL ${company.cuit}` : 'Sin CUIT/CUIL'}
                          {company.localidad && ` · ${company.localidad}`}
                          {company.provincia && `, ${company.provincia}`}
                        </span>
                      </div>
                    </CompanyName>
                    <CompanyRoles>
                      {roles.map((role) => (
                        <span key={`${company.id}-${role}`}>
                          {role === 'Proveedor' && <TbBuildingStore aria-hidden="true" />}
                          {role}
                        </span>
                      ))}
                      {!roles.length && <span>Sin rol asignado</span>}
                    </CompanyRoles>
                    <Button
                      type="button"
                      $variant="secondary"
                      onClick={() => startEditing(company)}
                      aria-label={`Editar ${company.razon_social}`}
                    >
                      <TbEdit aria-hidden="true" /> Editar
                    </Button>
                  </CompanyItem>
                );
              })}
            </CompanyList>
          ) : (
            <p>Todavía no hay empresas registradas.</p>
          )}
        </Panel>
      </CompanyGrid>
    </>
  );
};

export default Companies;
