# Arquitectura del Frontend - SGUL

## 1. Stack Tecnológico

El frontend se construirá con un enfoque que prioriza la eficiencia, la mantenibilidad y una experiencia de usuario moderna.

*   **Framework Principal:** Aunque el backend usa Django, el frontend se desarrollará con un enfoque desacoplado o híbrido.
*   **Lenguaje:** **JavaScript (ES6+)** o **TypeScript** para un código más robusto y escalable.
*   **Estilos:** **Sass** o **CSS Modules** para escribir CSS modular y organizado.
*   **Proceso de Build:** **Vite** o **Webpack** se utilizarán como empaquetadores de activos para optimizar, minificar y empaquetar el código CSS y JavaScript.

## 2. Estructura de Archivos

*   **Plantillas HTML Base:** Las plantillas principales de Django (`base.html`) servirán como punto de entrada para los activos compilados.
*   **Código Fuente del Frontend:** Se creará un nuevo directorio `frontend/` en la raíz del proyecto para alojar todo el código fuente de JavaScript y Sass, separado de la lógica de Django.

## 3. Principios de Arquitectura y Diseño

El frontend se desarrollará siguiendo estos principios clave:

### 1. Lógica Centralizada en el Backend
*   **Principio:** El frontend no duplicará la lógica de negocio. Será un consumidor de la lógica expuesta por el backend a través de una API.
*   **Implementación:** Para funcionalidades con cálculos complejos, como la planilla de empleados, el frontend no contendrá la fórmula. En su lugar, enviará los datos de entrada al endpoint `/api/payroll/calculate/` del backend y mostrará el resultado devuelto. Esto asegura una **única fuente de verdad** para la lógica de negocio.

### 2. Experiencia de Usuario Dinámica (SPA/Híbrida)
*   **Principio:** La interacción del usuario será fluida y rápida, minimizando las recargas de página completas.
*   **Implementación:** Se utilizará la **API Fetch** de JavaScript (AJAX) para las operaciones CRUD (Crear, Leer, Actualizar, Borrar). Por ejemplo:
    *   Al añadir una nueva observación a un lead, se enviarán los datos al backend en segundo plano y la nueva observación se añadirá a la lista en la interfaz de forma instantánea.
    *   Los formularios se procesarán de forma asíncrona, mostrando mensajes de éxito o error sin necesidad de una redirección.

### 3. Rendimiento Optimizado
*   **Principio:** Los tiempos de carga de la aplicación serán mínimos.
*   **Implementación:** Todo el código CSS y JavaScript pasará por un proceso de **build** (usando Vite/Webpack) que lo optimizará para producción. Esto incluye minificación, tree-shaking y empaquetado (bundling).

Siguiendo estos principios, el resultado será una aplicación web que se siente como una **Aplicación de Página Única (SPA)** o una **Aplicación Híbrida**, en lugar de un sitio web tradicional, ofreciendo una experiencia de usuario superior.
