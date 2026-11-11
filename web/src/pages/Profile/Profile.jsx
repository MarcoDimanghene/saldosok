import { useState } from 'react';
import styled from 'styled-components';
import { Button } from '../../component/ui/UIComponents';
import { CONDICIONES_IVA } from '../../config/appConfig';
import { useAuth } from '../../hook/useAuth';

const ProfileContainer = styled.div`
  max-width: 760px;
`;

const ProfileCard = styled.section`
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  background: #101827;
  color: #fff;
`;

const ProfileForm = styled.form`
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

const ProfileField = styled.label`
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.9rem;

  input,
  select {
    width: 100%;
    padding: 0.7rem 0.8rem;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 8px;
    background: #0b1220;
    color: #fff;
  }
`;

const ProfileMessage = styled.p`
  margin: 0.5rem 0 1rem;
  color: ${({ $error }) => ($error ? '#fecaca' : '#a7f3d0')};
`;

const Profile = () => {
  const { tenant, updateTenant } = useAuth();
  const [form, setForm] = useState({
    razon_social: tenant?.razon_social || '',
    cuit: tenant?.cuit || '',
    condicion_iva: tenant?.condicion_iva || '',
    domicilio: tenant?.domicilio || '',
  });
  const [message, setMessage] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const setField = (field) => (event) => {
    const value = field === 'cuit'
      ? event.target.value.replace(/\D/g, '').slice(0, 11)
      : event.target.value;
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage(null);
    if (!/^\d{11}$/.test(form.cuit)) {
      setMessage({ error: true, text: 'El CUIT debe tener 11 dígitos, sin guiones.' });
      return;
    }
    if (form.razon_social.trim().length < 2) {
      setMessage({ error: true, text: 'Ingresa una razón social válida.' });
      return;
    }

    setIsSaving(true);
    try {
      await updateTenant({
        cuit: form.cuit,
        razon_social: form.razon_social.trim(),
        condicion_iva: form.condicion_iva.trim() || null,
        domicilio: form.domicilio.trim() || null,
      });
      setMessage({ error: false, text: 'El perfil de organización se guardó correctamente.' });
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo guardar el perfil.' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <ProfileContainer>
      <h1>Perfil de organización</h1>
      <p>
        Estos son los datos fiscales de tu organización. Los emisores se administran en Empresas
        y podés elegirlos en cada factura de venta.
      </p>
      {message && (
        <ProfileMessage $error={message.error} role={message.error ? 'alert' : 'status'}>
          {message.text}
        </ProfileMessage>
      )}
      <ProfileCard>
        <h2>Datos fiscales de la organización (opcional)</h2>
        <ProfileForm onSubmit={handleSubmit}>
          <ProfileField>
            Razón social
            <input
              value={form.razon_social}
              onChange={setField('razon_social')}
              autoComplete="organization"
              maxLength={150}
              required
            />
          </ProfileField>
          <ProfileField>
            CUIT
            <input
              value={form.cuit}
              onChange={setField('cuit')}
              inputMode="numeric"
              autoComplete="off"
              maxLength={11}
              required
            />
          </ProfileField>
          <ProfileField>
            Condición frente al IVA
            <select
              value={form.condicion_iva}
              onChange={setField('condicion_iva')}
            >
              <option value="">Seleccionar condición (opcional)</option>
              {form.condicion_iva && !CONDICIONES_IVA.includes(form.condicion_iva) && (
                <option value={form.condicion_iva}>{form.condicion_iva}</option>
              )}
              {CONDICIONES_IVA.map((condition) => (
                <option key={condition} value={condition}>{condition}</option>
              ))}
            </select>
          </ProfileField>
          <ProfileField>
            Domicilio
            <input
              value={form.domicilio}
              onChange={setField('domicilio')}
              autoComplete="street-address"
              maxLength={255}
            />
          </ProfileField>
          <Button type="submit" disabled={isSaving}>
            {isSaving ? 'Guardando…' : 'Guardar perfil'}
          </Button>
        </ProfileForm>
      </ProfileCard>
    </ProfileContainer>
  );
};

export default Profile;
