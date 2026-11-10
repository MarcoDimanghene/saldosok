import assert from 'node:assert/strict';
import test from 'node:test';
import {
  loginInitialValues,
  validateLogin,
} from '../src/pages/Login/loginValidation.js';

test('login validation accepts a username and non-empty password', () => {
  assert.deepEqual(
    validateLogin({ username: 'ana', password: 'secret' }),
    {},
  );
});

test('login validation requires a username and password', () => {
  const errors = validateLogin({ ...loginInitialValues });

  assert.equal(errors.username, 'Ingresa tu nombre de usuario o correo electrónico.');
  assert.equal(errors.password, 'Ingresa tu contraseña.');
});
