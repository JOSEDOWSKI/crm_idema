# Arquitectura del Backend - SGUL

## 1. Stack Tecnológico

*   **Lenguaje:** Python 3.10+
*   **Framework:** Django 5.0+ y Django Rest Framework (DRF)
*   **Base de Datos:** PostgreSQL
*   **Tareas Asincrónicas:** Celery con Redis o RabbitMQ como message broker.
*   **Servidor de Aplicaciones:** Gunicorn
*   **Contenerización:** Docker y Docker Compose

## 2. Arquitectura General

El backend está diseñado bajo una arquitectura **headless**, lo que significa que su única responsabilidad es exponer una **API RESTful** segura y eficiente. No renderiza plantillas HTML directamente. Toda la lógica de negocio, validaciones y automatizaciones residen aquí, sirviendo como la única fuente de verdad para todos los clientes (frontend web, aplicación móvil, etc.).

## 3. Entidades y Serializers

Los modelos de Django (`gestion/models.py`) definen la estructura de la base de datos. Para cada modelo principal, se creará un **Serializer** de DRF que controlará la representación JSON de los datos en la API.

*   **Ejemplo de Serializer (`LeadSerializer`):**
    ```python
    class LeadSerializer(serializers.ModelSerializer):
        class Meta:
            model = Lead
            fields = ['id_lead', 'nombre_completo', 'telefono', 'estado_lead', 'fecha_ingreso']
    ```

## 4. Endpoints Principales de la API

La API se estructurará por recursos. A continuación, algunos ejemplos de endpoints clave:

*   `POST /api/token/`: Obtiene un token de autenticación (ej. JWT).
*   `GET, POST /api/leads/`: Lista todos los leads o crea uno nuevo.
*   `GET, PUT, DELETE /api/leads/<id>/`: Obtiene, actualiza o elimina un lead específico.
*   `GET /api/empleados/`: Lista los empleados.
*   `GET /api/programas/`: Lista los programas académicos.
*   `POST /api/matriculas/`: Crea una nueva matrícula (proceso de conversión de lead).
*   `GET /api/finanzas/balance/?sede_id=1`: Obtiene un resumen financiero para una sede específica.

## 5. Lógica de Negocio y Tareas Asincrónicas

*   **Automatizaciones en Modelos:** La lógica de negocio crítica (como la creación automática de `Ingresos` y `Gastos`) se mantendrá en los métodos `save()` de los modelos de Django para garantizar la consistencia de los datos, sin importar cómo se acceda a ellos.
*   **Tareas Asincrónicas (Celery):** Para operaciones que pueden ser lentas o que no necesitan ser instantáneas, se utilizará Celery.
    *   **Envío de Notificaciones Push:** Cuando se deba notificar a un alumno, se encolará una tarea en Celery para que un worker la procese en segundo plano, sin hacer esperar al usuario.
    *   **Generación de Reportes:** La generación de reportes financieros complejos se ejecutará como una tarea asincrónica.
    *   **Envío de Correos Masivos.**

## 6. Configuración y Despliegue (Docker)

El entorno de desarrollo y producción estará completamente containerizado con Docker. El archivo `docker-compose.yml` orquestará los servicios:
*   Un contenedor para la **aplicación de Django (Gunicorn)**.
*   Un contenedor para la **base de datos PostgreSQL**.
*   Un contenedor para el **broker de Celery (Redis)**.
*   Un contenedor para los **workers de Celery**.

Esto asegura que el entorno de desarrollo sea idéntico al de producción, eliminando problemas de consistencia.
