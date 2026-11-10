export const registerInitialValues = {
  nombre: '',
  dni: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  plan: 'basico',
};

export function validateRegister(values) {
  const errors = {};

  if (!values.nombre.trim()) errors.nombre = 'Ingresa tu nombre.';
  if (values.dni && !/^\d{7,8}$/.test(values.dni)) {
    errors.dni = 'El DNI debe tener 7 u 8 dígitos, sin puntos.';
  }
  if (!/^[a-zA-Z0-9_.-]{3,50}$/.test(values.username.trim())) {
    errors.username = 'Usa entre 3 y 50 letras, números, puntos, guiones o guiones bajos.';
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim())) {
    errors.email = 'Ingresa un correo electrónico válido.';
  }
  if (values.password.length < 6) {
    errors.password = 'La contraseña debe tener al menos 6 caracteres.';
  } else if (values.password.length > 128) {
    errors.password = 'La contraseña no puede superar los 128 caracteres.';
  }
  if (values.password !== values.confirmPassword) {
    errors.confirmPassword = 'Las contraseñas no coinciden.';
  }
  if (!['basico', 'moderado', 'premium'].includes(values.plan)) {
    errors.plan = 'Selecciona un plan válido.';
  }

  return errors;
}
