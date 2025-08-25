# Arquitectura de la Aplicación Móvil - SGUL

## 1. Stack Tecnológico

Para optimizar el tiempo de desarrollo y mantener una base de código unificada, la aplicación móvil se desarrollará como una **aplicación multiplataforma**.

*   **Framework:** React Native
*   **Plataforma de Desarrollo:** Expo para simplificar el proceso de build y despliegue en iOS y Android.
*   **Lenguaje:** TypeScript
*   **Comunicación API:** Axios o la Fetch API nativa para consumir la misma API REST del backend de Django que utiliza el frontend web.

## 2. Arquitectura General

La aplicación móvil será un cliente puro de la API del backend. Al compartir la misma API que el frontend web, se reutiliza toda la lógica de negocio y se asegura la consistencia de los datos.

*   **Navegación:** Se utilizará `React Navigation` para gestionar las pantallas y la navegación dentro de la aplicación.
*   **Componentes Nativos:** React Native renderizará componentes 100% nativos de iOS y Android, garantizando una experiencia de usuario fluida y familiar en cada plataforma.
*   **Acceso a Funcionalidades Nativas:** A través de Expo y las librerías de React Native, la aplicación tendrá acceso a funcionalidades del dispositivo como notificaciones push, cámara, etc.

## 3. Funcionalidades Clave

*   **Autenticación:** Login seguro contra la API del backend.
*   **Consulta de Información:** Acceso a notas, asistencias, horarios y pagos.
*   **Notificaciones Push:**
    *   **Implementación:** Se utilizará el servicio de **Expo Push Notifications**, que simplifica la integración con Firebase Cloud Messaging (FCM) para Android y Apple Push Notification service (APNs) para iOS.
    *   **Flujo:** El backend enviará las notificaciones a los servidores de Expo, y estos se encargarán de entregarlas a los dispositivos correspondientes.
*   **Gestión de Trámites:**
    *   Los estudiantes podrán iniciar y dar seguimiento a trámites administrativos directamente desde la app.
    *   La app consumirá los endpoints `/api/procedures/` que expondrá el backend para esta funcionalidad.

## 4. Ventajas del Enfoque Multiplataforma

*   **Base de Código Única:** Se escribe el código una vez en JavaScript/TypeScript y funciona tanto en iOS como en Android.
*   **Desarrollo Rápido:** El desarrollo es más rápido y económico que mantener dos equipos y dos bases de código nativas separadas.
*   **Consistencia:** Se reutiliza el 100% de la lógica del backend, garantizando que los datos y las reglas de negocio sean siempre los mismos en la web y en el móvil.
