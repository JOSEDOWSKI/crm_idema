# SGUL - Sistema de Gestión Universitaria

## 1. Resumen del Proyecto

El Sistema de Gestión Universitaria (SGUL) es una aplicación web integral diseñada para administrar las operaciones académicas, financieras y de recursos humanos de una institución educativa. El sistema está preparado para un entorno multi-sede, centralizando la gestión de todo el ciclo de vida del estudiante, desde que es un prospecto (lead) hasta su conversión a cliente y su gestión académica.

El núcleo del sistema se basa en la automatización de procesos clave para garantizar la integridad de los datos y proporcionar una visión clara de la salud financiera de cada sede.

## 2. Funcionalidades Principales

*   **Gestión de CRM y Ventas:**
    *   Registro y seguimiento de leads.
    *   Historial de interacciones y observaciones por lead.
    *   Conversión de leads a clientes con creación de matrícula.

*   **Gestión Académica:**
    *   Gestión de programas académicos y mallas curriculares.
    *   Registro de matrículas y seguimiento del estado del alumno (activo, retirado, etc.).
    *   Gestión de notas y asistencias por curso.

*   **Gestión Financiera Multi-Sede:**
    *   Registro de pagos de matrículas y pensiones.
    *   **Automatización de Ingresos:** Los pagos de los alumnos se registran automáticamente como ingresos en la sede correspondiente (virtual o presencial).
    *   **Automatización de Gastos:** Los pagos de planilla a empleados se registran automáticamente como gastos en la sede del empleado.
    *   Panel financiero para visualizar el balance de ingresos y gastos por sede.

*   **Recursos Humanos (RRHH):**
    *   Gestión de empleados y asignación a sedes.
    *   Sistema de cálculo de planilla (sueldo, bonos, descuentos, AFP).
    *   Control de acceso robusto basado en roles y permisos.

## 3. Stack Tecnológico General

*   **Backend:** Python, Django, PostgreSQL, Gunicorn.
*   **Frontend:** Django Templates (HTML, CSS), JavaScript.
*   **Aplicación Móvil (Propuesta):**
    *   **iOS:** Swift, SwiftUI.
    *   **Android:** Kotlin, Jetpack Compose.

## 4. Estructura del Proyecto

```
.
├── crm/                # Fichero de configuración del proyecto Django.
├── docs/               # Documentación adicional (backend, móvil).
├── gestion/            # App principal de Django, contiene toda la lógica.
│   ├── migrations/     # Migraciones de la base de datos.
│   ├── models.py       # Definición de todas las entidades de la base de datos.
│   ├── views.py        # Lógica de las vistas que renderizan las páginas.
│   ├── forms.py        # Formularios de Django.
│   ├── scripts/        # Scripts de utilidad para tareas administrativas.
│   └── templates/      # Plantillas HTML.
└── README.md           # Este documento.
```

## 5. Cómo Empezar (Desarrollo Local)

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_DIRECTORIO>
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la Base de Datos:**
    *   Asegúrate de tener PostgreSQL instalado y un servidor corriendo.
    *   Modifica `crm/settings.py` con tus credenciales de PostgreSQL.

5.  **Aplicar migraciones:**
    ```bash
    python manage.py migrate
    ```

6.  **Crear un superusuario:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Poblar datos iniciales (opcional pero recomendado):**
    *   Para tener roles y permisos básicos, ejecuta el script de seeding:
    ```bash
    python gestion/scripts/crear_roles_iniciales.py
    ```

8.  **Ejecutar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```

La aplicación estará disponible en `http://127.0.0.1:8000/`.