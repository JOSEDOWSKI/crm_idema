# Arquitectura del Frontend - SGUL

## 1. Stack Tecnológico Actual

El frontend del proyecto SGUL está construido con un enfoque tradicional de Django, directamente integrado con el backend.

*   **Lenguaje de Plantillas:** **Django Templates (HTML)**. La lógica de renderizado y el HTML se gestionan a través del sistema de plantillas de Django.
*   **Estilos:** **CSS plano**. Los estilos se escriben en archivos `.css` estándar.
*   **Interactividad:** **JavaScript plano (vanilla)**. Se utiliza para añadir funcionalidades dinámicas en el lado del cliente.

## 2. Estructura de Archivos

*   **Plantillas HTML:** Se encuentran en `gestion/templates/gestion/`. Cada vista de Django tiene asociada una plantilla HTML.
*   **Archivos Estáticos:** Se encuentran en `gestion/static/gestion/`.
    *   `*.css`: Contiene los estilos de la aplicación.
    *   `*.js`: Contiene la lógica de JavaScript.

## 3. Lógica de Frontend Destacada

La funcionalidad más compleja del frontend actual es el **cálculo de la planilla en tiempo real** en el formulario de creación/edición de empleados. Se utiliza JavaScript para escuchar los cambios en los campos de entrada (sueldo básico, bonos, horas extra, etc.) y actualizar los campos de "Remuneración Bruta" y "Neto Mensual" sin necesidad de recargar la página.

**Observación Importante:** Esta lógica de cálculo está **duplicada**. Existe una versión en JavaScript para la interactividad y otra en Python (`EmpleadoForm`) para el guardado y la validación en el backend.

## 4. Propuesta de Mejoras para Reconstrucción

Para modernizar el frontend, hacerlo más mantenible y mejorar la experiencia de usuario, se recomiendan las siguientes mejoras.

### 1. Centralizar la Lógica de Cálculo con una API
*   **Problema:** La duplicación de la lógica de cálculo de la planilla entre el frontend y el backend es una fuente potencial de errores.
*   **Solución:** Crear un endpoint en la API del backend (ej. `/api/payroll/calculate/`) que se encargue del cálculo. El frontend solo necesitaría enviar los datos de entrada a esta API mediante una petición `fetch` y mostrar el resultado devuelto. Esto asegura que la fórmula de cálculo resida en un único lugar (el backend).

### 2. Integrar un Proceso de Build Moderno
*   **Problema:** Servir archivos CSS y JS sin optimizar afecta negativamente el rendimiento y los tiempos de carga.
*   **Solución:** Adoptar un empaquetador de JavaScript/CSS como **Vite** o **Webpack**. Estas herramientas permiten:
    *   **Minificar** los archivos, reduciendo su tamaño.
    *   **Empaquetarlos (bundling)** en menos archivos para reducir el número de peticiones al servidor.
    *   Utilizar herramientas modernas como **Sass** para un CSS más organizado.

### 3. Mejorar la Experiencia de Usuario (UX) con AJAX
*   **Problema:** La aplicación requiere recargas de página completas para la mayoría de las acciones.
*   **Solución:** Utilizar la **API Fetch** de JavaScript (AJAX) para crear interacciones más fluidas y dinámicas. Por ejemplo:
    *   Al añadir una nueva observación a un lead, la observación debería aparecer en la lista instantáneamente sin recargar la página.
    *   Los formularios podrían enviar sus datos en segundo plano y mostrar mensajes de éxito o error sin una redirección completa.

Estas mejoras transformarían la aplicación de un sitio web tradicional a una **Aplicación de Página Única (SPA)** o una **Aplicación Híbrida**, mucho más rápida y agradable para el usuario.
