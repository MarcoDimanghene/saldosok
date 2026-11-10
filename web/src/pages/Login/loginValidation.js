export const loginInitialValues = {
  username: '',
  password: '',
};

export function validateLogin(values) {
  const errors = {};
  const username = values.username.trim();

  if (!username) {
    errors.username = 'Ingresa tu nombre de usuario o correo electrónico.';
  }

  if (!values.password) errors.password = 'Ingresa tu contraseña.';

  return errors;
}
