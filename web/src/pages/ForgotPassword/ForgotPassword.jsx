import { useState } from 'react';
import { Link } from 'react-router-dom';
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
import { resetPasswordWithRecoveryCode } from '../../services/authService';

const ForgotPassword = () => {
  const [recovery, setRecovery] = useState({
    username: '',
    recovery_code: '',
    new_password: '',
  });
  const [recoveryStatus, setRecoveryStatus] = useState(null);
  const [isRecovering, setIsRecovering] = useState(false);

  const handleRecoverySubmit = async (event) => {
    event.preventDefault();
    setRecoveryStatus(null);
    setIsRecovering(true);
    try {
      const result = await resetPasswordWithRecoveryCode({
        ...recovery,
        username: recovery.username.trim(),
      });
      setRecoveryStatus({
        error: false,
        message: result.message,
        recoveryCode: result.recovery_code,
      });
      setRecovery({ username: '', recovery_code: '', new_password: '' });
    } catch (error) {
      setRecoveryStatus({ error: true, message: error.message || 'No se pudo restablecer la contraseña.' });
    } finally {
      setIsRecovering(false);
    }
  };

  return (
    <LoginContainer>
      <LoginCard>
        <LoginTitle>Recuperar contraseña</LoginTitle>
        <LoginDescription>
          La recuperación por correo está desactivada. Usa el código de recuperación de administrador o solicita
          al administrador de tu espacio que cambie tu contraseña.
        </LoginDescription>

        <LoginForm onSubmit={handleRecoverySubmit} style={{ marginTop: '2rem' }}>
          <h2>Usar código de recuperación</h2>
          <FormField>
            <FormLabel htmlFor="recovery-username">Usuario administrador</FormLabel>
            <FormInput
              id="recovery-username"
              autoComplete="username"
              value={recovery.username}
              onChange={(event) => setRecovery({ ...recovery, username: event.target.value })}
              required
            />
          </FormField>
          <FormField>
            <FormLabel htmlFor="recovery-code">Código de recuperación</FormLabel>
            <FormInput
              id="recovery-code"
              autoComplete="off"
              value={recovery.recovery_code}
              onChange={(event) => setRecovery({ ...recovery, recovery_code: event.target.value })}
              required
            />
          </FormField>
          <FormField>
            <FormLabel htmlFor="recovery-password">Nueva contraseña</FormLabel>
            <FormInput
              id="recovery-password"
              type="password"
              autoComplete="new-password"
              minLength={6}
              maxLength={128}
              value={recovery.new_password}
              onChange={(event) => setRecovery({ ...recovery, new_password: event.target.value })}
              required
            />
          </FormField>
          {recoveryStatus && (
            <div role={recoveryStatus.error ? 'alert' : 'status'}>
              <p>{recoveryStatus.message}</p>
              {recoveryStatus.recoveryCode && (
                <p>
                  Nuevo código: <strong>{recoveryStatus.recoveryCode}</strong>
                </p>
              )}
            </div>
          )}
          <SubmitButton type="submit" disabled={isRecovering}>
            {isRecovering ? 'Restableciendo…' : 'Restablecer con código'}
          </SubmitButton>
        </LoginForm>

        <LoginLinks>
          <LoginLink as={Link} to="/login">Volver a iniciar sesión</LoginLink>
        </LoginLinks>
      </LoginCard>
    </LoginContainer>
  );
};

export default ForgotPassword;
