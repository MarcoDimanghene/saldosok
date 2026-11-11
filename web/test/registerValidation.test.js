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
  email: 'ana@example.com',
  password: 'password123',
  confirmPassword: 'password123',
};

test('register validation accepts valid account data', () => {
  assert.deepEqual(validateRegister(validRegistration), {});
});

test('register validation requires an email', () => {
  assert.equal(
    validateRegister({ ...validRegistration, email: '' }).email,
    'Ingresa un correo electrónico válido.',
  );
});

test('register validation reports invalid email and mismatched passwords', () => {
  const errors = validateRegister({
    ...validRegistration,
    email: 'not-an-email',
    confirmPassword: 'different',
  });

  assert.equal(errors.email, 'Ingresa un correo electrónico válido.');
  assert.equal(errors.confirmPassword, 'Las contraseñas no coinciden.');
});

test('register validation enforces backend password limits', () => {
  const errors = validateRegister({
    ...validRegistration,
    password: 'short',
    confirmPassword: 'short',
  });

  assert.equal(errors.password, 'La contraseña debe tener al menos 6 caracteres.');
});
