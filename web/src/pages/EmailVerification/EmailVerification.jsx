import { useEffect, useRef, useState } from 'react';
import { Formik } from 'formik';
import { Link, useLocation, useSearchParams } from 'react-router-dom';
import { resendEmailVerification, verifyEmail } from '../../services/authService';
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

const EmailVerification = () => {
  const [searchParams] = useSearchParams();
  const { state } = useLocation();
  const token = searchParams.get('token');
  const [verificationStatus, setVerificationStatus] = useState({
    loading: Boolean(token),
    error: false,
    message: token ? 'Validando el enlace…' : '',
  });
  const [resendStatus, setResendStatus] = useState(null);
  const verificationStarted = useRef(false);

  useEffect(() => {
    if (!token || verificationStarted.current) return;
    verificationStarted.current = true;
    verifyEmail(token)
      .then((result) => setVerificationStatus({
        loading: false,
        error: false,
        message: result.message,
      }))
      .catch((error) => setVerificationStatus({
        loading: false,
        error: true,
        message: error.message || 'No se pudo confirmar el correo.',
      }));
  }, [token]);

  const handleResend = async (values, { setSubmitting }) => {
    setResendStatus(null);
    try {
      const result = await resendEmailVerification(values.email.trim());
      setResendStatus({ error: false, message: result.message });
    } catch (error) {
      setResendStatus({
        error: true,
        message: error.message || 'No se pudo solicitar un nuevo enlace.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <LoginContainer>
      <LoginCard>
        <LoginTitle>{token ? 'Confirmación de correo' : 'Confirma tu correo (opcional)'}</LoginTitle>
        <LoginDescription>
          {token
            ? verificationStatus.message
            : 'Confirmar el correo es opcional para ingresar, pero permite recuperar la contraseña mediante un enlace.'}
        </LoginDescription>

        {verificationStatus.error && (
          <p role="alert" style={{ color: '#fda4af', marginBottom: '1rem' }}>
            {verificationStatus.message}
          </p>
        )}
        {verificationStatus.loading && <p role="status">{verificationStatus.message}</p>}
        {!token && (
          <Formik
            initialValues={{ email: state?.email || '' }}
            onSubmit={handleResend}
          >
            {({ values, handleChange, isSubmitting, handleSubmit }) => (
              <LoginForm onSubmit={handleSubmit}>
                <FormField>
                  <FormLabel htmlFor="verification-email">Correo electrónico</FormLabel>
                  <FormInput
                    id="verification-email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    value={values.email}
                    onChange={handleChange}
                    required
                  />
                </FormField>
                {resendStatus && (
                  <p
                    role={resendStatus.error ? 'alert' : 'status'}
                    style={{ color: resendStatus.error ? '#fda4af' : '#5eead4' }}
                  >
                    {resendStatus.message}
                  </p>
                )}
                <SubmitButton type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Enviando…' : 'Reenviar enlace'}
                </SubmitButton>
              </LoginForm>
            )}
          </Formik>
        )}

        <LoginLinks>
          <LoginLink as={Link} to="/login">Ir a iniciar sesión</LoginLink>
        </LoginLinks>
      </LoginCard>
    </LoginContainer>
  );
};

export default EmailVerification;
