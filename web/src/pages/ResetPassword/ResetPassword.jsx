import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  FormField,
  FormInput,
  FormLabel,
  LoginCard,
  LoginContainer,
  LoginDescription,
  LoginForm,
  LoginLink,
  LoginLinks,
  LoginTitle,
  SubmitButton,
} from '../Login/Login.styles';
import { resetPassword } from '../../services/authService';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [status, setStatus] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus(null);
    if (password !== confirmation) {
      setStatus({ error: true, message: 'Las contraseñas no coinciden.' });
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await resetPassword(token, password);
      setStatus({ error: false, message: result.message });
      setPassword('');
      setConfirmation('');
    } catch (error) {
      setStatus({ error: true, message: error.message || 'No se pudo cambiar la contraseña.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <LoginContainer>
      <LoginCard>
        <LoginTitle>Crear nueva contraseña</LoginTitle>
        <LoginDescription>
          El enlace es de un solo uso y vence en el plazo indicado en el correo.
        </LoginDescription>
        <LoginForm onSubmit={handleSubmit}>
          <FormField>
            <FormLabel htmlFor="new-password">Nueva contraseña</FormLabel>
            <FormInput
              id="new-password"
              type="password"
              autoComplete="new-password"
              minLength={6}
              maxLength={128}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </FormField>
          <FormField>
            <FormLabel htmlFor="confirm-password">Confirmar contraseña</FormLabel>
            <FormInput
              id="confirm-password"
              type="password"
              autoComplete="new-password"
              minLength={6}
              maxLength={128}
              value={confirmation}
              onChange={(event) => setConfirmation(event.target.value)}
              required
            />
          </FormField>
          {status && <p role={status.error ? 'alert' : 'status'}>{status.message}</p>}
          <SubmitButton type="submit" disabled={isSubmitting || !token}>
            {isSubmitting ? 'Guardando…' : 'Guardar contraseña'}
          </SubmitButton>
        </LoginForm>
        <LoginLinks>
          <LoginLink as={Link} to="/login">Volver a iniciar sesión</LoginLink>
        </LoginLinks>
      </LoginCard>
    </LoginContainer>
  );
};

export default ResetPassword;
