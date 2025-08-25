# Propuesta para Aplicación Móvil - SGUL

## 1. Objetivo General

Desarrollar una aplicación móvil nativa para iOS y Android que ofrezca a los estudiantes una experiencia fluida y directa para interactuar con los servicios académicos y administrativos de la institución, mejorando la comunicación y el acceso a la información.

## 2. Stack Tecnológico Propuesto

Para garantizar el mejor rendimiento, experiencia de usuario y acceso a las funcionalidades nativas de cada plataforma, se propone el siguiente stack:

*   **iOS:**
    *   **Lenguaje:** Swift
    *   **UI Framework:** SwiftUI
*   **Android:**
    *   **Lenguaje:** Kotlin
    *   **UI Framework:** Jetpack Compose
*   **Comunicación con Backend:**
    *   La aplicación móvil consumirá una **API REST** que deberá ser construida en el backend de Django. Esta API será la única fuente de verdad para la aplicación.

## 3. Funcionalidades

El desarrollo se puede planificar en dos fases principales.

### Fase 1: Consulta de Información Académica

El objetivo de esta fase es dar al alumno acceso de solo lectura a su información más importante.

*   **Autenticación:** Login de usuario y contraseña para estudiantes.
*   **Dashboard del Estudiante:** Una pantalla principal que resuma la información más relevante.
*   **Mis Notas:** Vista para consultar las calificaciones obtenidas en cada curso y periodo.
*   **Mi Asistencia:** Vista para consultar el historial de asistencias a clases.
*   **Mi Horario:** Visualización de la malla curricular y los cursos correspondientes a su ciclo actual.
*   **Mis Pagos:** Historial de los pagos de matrícula y pensiones realizados.

### Fase 2: Notificaciones y Trámites (Funcionalidad Interactiva)

Esta fase se centra en la comunicación bidireccional y en la gestión de servicios.

*   **Notificaciones Push:**
    *   **Requerimiento Backend:** Integrar un servicio como **Firebase Cloud Messaging (FCM)** en el backend de Django.
    *   **Casos de Uso:**
        *   Anuncios generales de la institución.
        *   Notificación de una nueva calificación publicada.
        *   Recordatorios de pagos de pensión.
        *   Alertas sobre inasistencias.
        *   Confirmación de trámites iniciados o completados.

*   **Gestión de Trámites:**
    *   **Requerimiento Backend:** Desarrollar nuevos modelos y vistas en Django para definir y gestionar diferentes tipos de trámites (ej. `Solicitud`, `EstadoTramite`).
    *   **Flujo de Usuario:**
        1.  El estudiante selecciona un tipo de trámite desde la app (ej. "Solicitar Constancia de Estudios").
        2.  Rellena un formulario simple y lo envía.
        3.  Puede ver una lista de sus trámites y el estado actual de cada uno ("Recibido", "En Proceso", "Listo para Recoger", "Rechazado").
        4.  Recibe una notificación push cuando el estado de su trámite cambia.

## 4. Requisitos de la API Backend

Para que la aplicación móvil funcione, el backend de Django deberá exponer una serie de endpoints RESTful, por ejemplo:

*   `POST /api/auth/token/`: Para el login de usuarios.
*   `GET /api/student/profile/`: Devuelve los datos del perfil del estudiante.
*   `GET /api/student/grades/`: Devuelve las notas del estudiante.
*   `GET /api/student/attendance/`: Devuelve las asistencias del estudiante.
*   `POST /api/student/device/`: Registra el token del dispositivo para las notificaciones push.
*   `GET /api/procedures/`: Lista los trámites disponibles.
*   `POST /api/procedures/submit/`: Para que el estudiante inicie un nuevo trámite.
*   `GET /api/procedures/status/`: Para consultar el estado de sus trámites.
