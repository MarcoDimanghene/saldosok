import { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { verifyEmail } from '../../services/authService';
import {
  LoginCard,
  LoginContainer,
  LoginDescription,
  LoginLink,
  LoginLinks,
  LoginTitle,
} from '../Login/Login.styles';

const EmailVerification = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [verificationStatus, setVerificationStatus] = useState({
    loading: Boolean(token),
    error: false,
    message: token ? 'Validando el enlace…' : '',
  });
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

  return (
    <LoginContainer>
      <LoginCard>
        <LoginTitle>Confirmación de correo</LoginTitle>
        <LoginDescription>
          {token
            ? verificationStatus.message
            : 'La confirmación y los envíos por correo están desactivados. Puedes iniciar sesión con tu usuario y contraseña.'}
        </LoginDescription>

        {verificationStatus.error && (
          <p role="alert" style={{ color: '#fda4af', marginBottom: '1rem' }}>
            {verificationStatus.message}
          </p>
        )}
        {verificationStatus.loading && <p role="status">{verificationStatus.message}</p>}
        <LoginLinks>
          <LoginLink as={Link} to="/login">Ir a iniciar sesión</LoginLink>
        </LoginLinks>
      </LoginCard>
    </LoginContainer>
  );
};

export default EmailVerification;
