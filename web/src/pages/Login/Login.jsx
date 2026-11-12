import { ErrorMessage, Field, Formik } from 'formik';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hook/useAuth';
import {
  FieldError,
  FormError,
  FormField,
  FormInput,
  FormLabel,
  LoginBrand,
  LoginCard,
  LoginContainer,
  LoginDescription,
  LoginForm,
  LoginLink,
  LoginLinks,
  LoginTitle,
  SubmitButton,
} from './Login.styles';
import { loginInitialValues, validateLogin } from './loginValidation';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (values, { setStatus }) => {
    try {
      await login(values.username.trim(), values.password);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      setStatus(error.message || 'No se pudo iniciar sesión. Intenta nuevamente.');
    }
  };

  return (
    <LoginContainer>
      <LoginCard>
        <LoginBrand>SALDOS OK</LoginBrand>
        <LoginTitle>Iniciar sesión</LoginTitle>
        <LoginDescription>Ingresa con tu cuenta para continuar.</LoginDescription>

        <Formik
          initialValues={loginInitialValues}
          validate={validateLogin}
          onSubmit={handleSubmit}
        >
          {({ status, isSubmitting, handleSubmit: submitForm }) => (
            <LoginForm onSubmit={submitForm}>
              <FormField>
                <FormLabel htmlFor="username">Usuario o correo electrónico</FormLabel>
                <Field name="username">
                  {({ field, meta }) => {
                    const hasError = Boolean(meta.touched && meta.error);
                    return (
                      <FormInput
                        {...field}
                        id="username"
                        type="text"
                        autoComplete="username"
                        aria-invalid={hasError || undefined}
                        aria-describedby={hasError ? 'username-error' : undefined}
                        required
                      />
                    );
                  }}
                </Field>
                <ErrorMessage name="username" component={FieldError} id="username-error" />
              </FormField>

              <FormField>
                <FormLabel htmlFor="password">Contraseña</FormLabel>
                <Field name="password">
                  {({ field, meta }) => {
                    const hasError = Boolean(meta.touched && meta.error);
                    return (
                      <FormInput
                        {...field}
                        id="password"
                        type="password"
                        autoComplete="current-password"
                        aria-invalid={hasError || undefined}
                        aria-describedby={hasError ? 'password-error' : undefined}
                        required
                      />
                    );
                  }}
                </Field>
                <ErrorMessage name="password" component={FieldError} id="password-error" />
              </FormField>

              {status && <FormError role="alert">{status}</FormError>}

              <SubmitButton type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Ingresando...' : 'Ingresar'}
              </SubmitButton>
            </LoginForm>
          )}
        </Formik>

        <LoginLinks>
          <LoginLink to="/forgot-password">¿Olvidaste tu contraseña?</LoginLink>
          <LoginLink to="/verify-email">Confirmar correo para recuperación</LoginLink>
        </LoginLinks>
      </LoginCard>
    </LoginContainer>
  );
};

export default Login;
