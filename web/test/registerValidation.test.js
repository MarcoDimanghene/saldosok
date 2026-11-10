import assert from 'node:assert/strict';
import test from 'node:test';
import {
  registerInitialValues,
  validateRegister,
} from '../src/pages/Register/registerValidation.js';

const validRegistration = {
  ...registerInitialValues,
  nombre: 'Ana Pérez',
  username: 'ana',
  razon_social: 'Empresa de prueba',
  cuit: '20123456789',
  condicion_iva: 'Responsable Inscripto',
  email: 'ana@example.com',
  password: 'password123',
  confirmPassword: 'password123',
};

test('register validation accepts valid company and account data', () => {
  assert.deepEqual(validateRegister(validRegistration), {});
});

test('register validation accepts an account without email', () => {
  assert.deepEqual(validateRegister({ ...validRegistration, email: '' }), {});
});

test('register validation reports invalid email, CUIT and mismatched passwords', () => {
  const errors = validateRegister({
    ...validRegistration,
    email: 'not-an-email',
    cuit: '123',
    confirmPassword: 'different',
  });

  assert.equal(errors.email, 'Ingresa un correo electrónico válido.');
  assert.equal(errors.cuit, 'El CUIT debe tener 11 dígitos, sin guiones.');
  assert.equal(errors.confirmPassword, 'Las contraseñas no coinciden.');
});

test('register validation enforces backend password and address limits', () => {
  const errors = validateRegister({
    ...validRegistration,
    password: 'short',
    confirmPassword: 'short',
    domicilio: 'x'.repeat(256),
  });

  assert.equal(errors.password, 'La contraseña debe tener al menos 6 caracteres.');
  assert.equal(errors.domicilio, 'El domicilio no puede superar los 255 caracteres.');
});
