# Arquitectura del Frontend - SGUL

## 1. Stack Tecnológico

El frontend será una **Single-Page Application (SPA)** moderna, completamente desacoplada del backend.

*   **Framework:** React.js (v18+)
*   **Lenguaje:** TypeScript
*   **Herramienta de Build:** Vite
*   **Estilos:** Tailwind CSS para un desarrollo de UI rápido y consistente.
*   **Gestión de Estado:** Redux Toolkit o Zustand (a definir) para manejar el estado global de la aplicación.
*   **Comunicación API:** Axios o la Fetch API nativa para comunicarse con el backend de Django Rest Framework.

## 2. Arquitectura General

El frontend es un cliente puro que consume la API del backend. Su única responsabilidad es la presentación y la experiencia de usuario. No contiene lógica de negocio.

*   **Enrutamiento:** Se utilizará `react-router-dom` para gestionar las rutas del lado del cliente (ej. `/leads`, `/dashboard`).
*   **Componentes:** La UI se construirá con una arquitectura de componentes reutilizables (ej. botones, tablas, modales).
*   **Autenticación:** Gestionará tokens de autenticación (ej. JWT) obtenidos de la API del backend para asegurar las rutas y las peticiones.

## 3. Flujo de Datos Típico

1.  El usuario navega a una ruta (ej. `/leads`).
2.  El componente de React correspondiente se renderiza.
3.  Se utiliza un hook (`useEffect`) para disparar una petición a la API del backend (`GET /api/leads/`).
4.  La respuesta de la API se guarda en el estado global de la aplicación.
5.  La interfaz se actualiza para mostrar los datos obtenidos.

## 4. Estructura de Directorios (Propuesta)

```
frontend/
├── public/
│   └── ... # Archivos estáticos públicos
├── src/
│   ├── api/          # Lógica para comunicarse con el backend
│   ├── components/   # Componentes reutilizables de UI
│   ├── features/     # Lógica y componentes por funcionalidad (leads, finanzas)
│   ├── hooks/        # Hooks personalizados de React
│   ├── pages/        # Componentes que representan páginas completas
│   ├── store/        # Configuración del estado global (Redux/Zustand)
│   ├── App.tsx       # Componente raíz
│   └── main.tsx      # Punto de entrada de la aplicación
├── .eslintrc.cjs
├── package.json
├── tailwind.config.js
└── vite.config.ts
```

## 5. Configuración y Despliegue (Docker)

El frontend se ejecutará en su propio contenedor de Docker, gestionado por Docker Compose.
*   **Desarrollo:** El contenedor utilizará el servidor de desarrollo de Vite con Hot-Module Replacement (HMR) para una experiencia de desarrollo instantánea.
*   **Producción:** El Dockerfile construirá una versión optimizada y estática de la aplicación (usando `npm run build`) y la servirá con un servidor web ligero como Nginx.
