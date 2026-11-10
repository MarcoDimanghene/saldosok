# Confirmación de correo y recuperación de contraseña

El correo es opcional y no bloquea el inicio de sesión. Si se informa uno, el backend envía un enlace de confirmación válido por 24 horas. Solo las cuentas con correo confirmado pueden solicitar recuperación de contraseña por email; los enlaces de recuperación vencen en una hora y solo se pueden usar una vez.

Al registrar la organización se muestra un código de recuperación de un solo uso para el administrador principal. Debe guardarse fuera de la aplicación; el servidor conserva únicamente su hash. Si se pierde el código y no hay correo confirmado, la recuperación deberá gestionarla un operador de la plataforma. El administrador puede cambiar las contraseñas de los usuarios de su equipo desde la sección Usuarios.

Configura estas variables en el `.env` de la raíz del proyecto:

```dotenv
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=cuenta@example.com
SMTP_PASSWORD=contraseña-de-aplicacion
SMTP_FROM=cuenta@example.com
SMTP_USE_TLS=true
FRONTEND_URL=http://localhost:5173
```

Para SMTP sobre SSL implícito utiliza el puerto `465`; en ese puerto el backend usa TLS directamente. `SMTP_USER` y `SMTP_PASSWORD` pueden omitirse si el servidor permite relay sin autenticación. No guardes credenciales en el repositorio.

Antes de desplegar estos cambios en una base existente, ejecuta desde la raíz:

```powershell
.\venv\Scripts\python.exe -m database.migrate_username_password_recovery
```

La migración agrega nombres de usuario a las cuentas existentes usando `usuario<ID>` y permite que el correo quede vacío. Las cuentas existentes pueden seguir iniciando sesión con su correo o usar el nombre de usuario asignado. Si SMTP no está configurado, el registro sigue funcionando y muestra el código de recuperación; la verificación y la recuperación por correo quedan disponibles cuando se configure SMTP.
