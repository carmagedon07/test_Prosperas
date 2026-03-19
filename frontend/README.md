
# Frontend de Procesamiento Asíncrono de Reportes

Este frontend implementa una SPA en React (Create React App) para interactuar con el backend de procesamiento asíncrono de reportes.

## Características
- Inicio de sesión con JWT
- Creación y visualización de trabajos (jobs) del usuario
- Polling automático hasta que todos los jobs estén finalizados
- Indicadores de estado con color e icono
- Accesibilidad básica (contraste, ARIA)
- Pruebas unitarias con Testing Library
- UI en español

## Estructura
- `src/components/`: Componentes reutilizables (JobList, JobItem, JobStatus, Loader, Navbar, JobForm)
- `src/pages/`: Páginas principales (LoginPage, Dashboard)
- `src/context/`: Contexto de autenticación
- `src/services/`: Llamadas a la API
- `src/hooks/`: Hooks personalizados (usePolling)
- `src/styles/`: CSS modular

## Instalación y ejecución

1. Instala dependencias:
	```bash
	npm install
	```
2. Crea un archivo `.env` si necesitas cambiar la URL del backend:
	```env
	REACT_APP_API_URL=http://localhost:8000
	```
3. Ejecuta la app:
	```bash
	npm start
	```

## Pruebas unitarias

```bash
npm test
```

## Notas
- El backend debe estar corriendo en http://localhost:8000 por defecto.
- Solo los usuarios con rol "admin" pueden ver todos los jobs. Otros usuarios solo ven los suyos.
- El polling se detiene automáticamente cuando todos los jobs están finalizados.

---
¿Dudas o sugerencias? Abre un issue o contacta al responsable del repositorio.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
