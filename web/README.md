# React + Vite

## Conexión con la API

En producción, el frontend usa `https://saldosok-back.vercel.app` por defecto.
Para cambiarla, configura `VITE_API_URL` en las variables de entorno del frontend
en Vercel y vuelve a desplegar. En desarrollo local, el valor predeterminado es
`http://localhost:8000`; puedes sobrescribirlo con `VITE_API_URL` en `web/.env`.

El backend debe tener `FRONTEND_URL` configurada en Vercel con el origen exacto
del frontend (por ejemplo, `https://mi-app.vercel.app`, sin una ruta al final)
para permitir las solicitudes del navegador.

`vercel.json` configura el fallback de rutas de la SPA a `index.html`, para que
secciones como `/dashboard` o `/imports` también funcionen al recargar la página.

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
