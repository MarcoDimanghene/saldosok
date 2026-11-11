import { ErrorMessage, Field, Formik } from 'formik';
import { useState } from 'react';
import { useAuth } from '../../hook/useAuth';
import {
  BackLink,
  FieldError,
  FieldsGrid,
  FormError,
  FormField,
  FormInput,
  FormLabel,
  RegisterCard,
  RegisterContainer,
  RegisterDescription,
  RegisterForm,
  RegisterTitle,
  SubmitButton,
} from './Register.styles';
import { registerInitialValues, validateRegister } from './registerValidation';

function RegisterField({
  name,
  label,
  as: Control = FormInput,
  onValueChange,
  children,
  ...controlProps
}) {
  return (
    <FormField>
      <FormLabel htmlFor={name}>{label}</FormLabel>
      <Field name={name}>
        {({ field, meta, form }) => {
          const hasError = Boolean(meta.touched && meta.error);
          return (
            <Control
              {...field}
              {...controlProps}
              id={name}
              aria-invalid={hasError || undefined}
              aria-describedby={hasError ? `${name}-error` : undefined}
              onChange={onValueChange
                ? (event) => onValueChange(event, form)
                : field.onChange}
            >
              {children}
            </Control>
          );
        }}
      </Field>
      <ErrorMessage name={name} component={FieldError} id={`${name}-error`} />
    </FormField>
  );
}

const Register = () => {
  const { register } = useAuth();
  const [registrationResult, setRegistrationResult] = useState(null);

  const handleSubmit = async (values, { setStatus }) => {
    try {
      const result = await register({
        nombre: values.nombre.trim(),
        dni: values.dni || null,
        username: values.username.trim(),
        email: values.email.trim(),
        password: values.password,
      });
      setRegistrationResult(result);
    } catch (error) {
      setStatus(error.message || 'No se pudo completar el registro. Intenta nuevamente.');
    }
  };

  return (
    <RegisterContainer>
      <RegisterCard>
        <RegisterTitle>Crear cuenta</RegisterTitle>
        <RegisterDescription>
          Crea la cuenta del titular para contratar SaldoOk. Después podrás completar el perfil de tu empresa.
        </RegisterDescription>

        {registrationResult ? (
          <>
            <RegisterDescription>{registrationResult.message}</RegisterDescription>
            <FormField>
              <FormLabel htmlFor="recovery-code">Código de recuperación (se muestra una sola vez)</FormLabel>
              <FormInput id="recovery-code" readOnly value={registrationResult.recovery_code} />
            </FormField>
            <RegisterDescription>
              Guarda este código en un lugar seguro. Si pierdes el acceso y no puedes recuperar por correo,
              lo necesitarás para cambiar la contraseña.
            </RegisterDescription>
            {registrationResult.user.email && (
              <BackLink to="/verify-email" state={{ email: registrationResult.user.email }}>
                Confirmar correo para habilitar la recuperación por email
              </BackLink>
            )}
            <BackLink to="/login">Ir a iniciar sesión</BackLink>
          </>
        ) : (
        <Formik
          initialValues={registerInitialValues}
          validate={validateRegister}
          onSubmit={handleSubmit}
        >
          {({
            status,
            isSubmitting,
            handleSubmit: submitForm,
          }) => (
            <RegisterForm onSubmit={submitForm}>
              <FieldsGrid>
                <RegisterField name="nombre" label="Tu nombre" autoComplete="name" required />
                <RegisterField
                  name="dni"
                  label="DNI (opcional)"
                  inputMode="numeric"
                  autoComplete="off"
                  maxLength={8}
                  onValueChange={(event, form) => form.setFieldValue(
                    'dni',
                    event.target.value.replace(/\D/g, '').slice(0, 8),
                  )}
                />
                <RegisterField name="username" label="Nombre de usuario" autoComplete="username" required />
                <RegisterField
                  name="email"
                  label="Correo electrónico"
                  type="email"
                  autoComplete="email"
                  required
                />
                <RegisterField
                  name="password"
                  label="Contraseña"
                  type="password"
                  autoComplete="new-password"
                  required
                />
                <RegisterField
                  name="confirmPassword"
                  label="Confirmar contraseña"
                  type="password"
                  autoComplete="new-password"
                  required
                />
              </FieldsGrid>

              {status && <FormError role="alert">{status}</FormError>}

              <SubmitButton type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Creando cuenta...' : 'Crear cuenta'}
              </SubmitButton>
              <BackLink to="/">Volver al inicio</BackLink>
            </RegisterForm>
          )}
        </Formik>
        )}
      </RegisterCard>
    </RegisterContainer>
  );
};

export default Register;
