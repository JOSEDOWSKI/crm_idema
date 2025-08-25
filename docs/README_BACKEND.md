# Arquitectura del Backend - SGUL

## 1. Stack Tecnológico

*   **Lenguaje:** Python 3.10+
*   **Framework:** Django 5.0+
*   **Base de Datos (Producción):** PostgreSQL
*   **Base de Datos (Desarrollo):** SQLite 3
*   **Servidor de Aplicaciones (Producción):** Gunicorn

## 2. Entidades Principales (Modelos)

El núcleo del sistema reside en `gestion/models.py`. Las entidades más importantes son:

*   **`Sede`**: Representa un campus (físico o virtual). Es la clave para la contabilidad por separado.
*   **`RolEmpleado` y `PermisoPersonalizado`**: Implementan un sistema de control de acceso (RBAC). Los permisos se definen como códigos (ej. `crear_lead`) y se asignan a roles.
*   **`Usuario`**: Modelo personalizado que se vincula al `User` de Django y a un `RolEmpleado`. Permite sobreescribir permisos a nivel de usuario.
*   **`Empleado`**: Contiene la información de RRHH y de planilla del personal. Se vincula a un `Usuario` y a una `Sede`.
*   **`Lead`**: Prospectos o clientes potenciales.
*   **`Cliente`**: Leads que han sido convertidos.
*   **`Matricula`**: Representa la inscripción de un `Cliente` a un `ProgramaAcademico`.
*   **`Pago`**: Registra los pagos de una `Matricula`.
*   **`Ingreso` y `Gasto`**: Registros contables generados a partir de `Pago` y `PlanillaEmpleado`, respectivamente. Se asocian a una `Sede`.
*   **`PlanillaEmpleado`**: Representa el pago de un sueldo a un `Empleado` en un mes/año específico.

## 3. Lógica de Negocio y Automatizaciones

La inteligencia del sistema se concentra en los métodos `save()` de los modelos y en los formularios.

*   **Observaciones Unificadas:** Al crear un `Lead` o `Matricula`, las observaciones iniciales se mueven a un modelo de historial (`ObservacionLead`, `ObservacionMatricula`) para que no se pierda información.
*   **Contabilidad Automática (Ingresos):** El método `Pago.save()` llama a `crear_ingreso_automatico()`, que genera un registro de `Ingreso` y lo atribuye a la sede correcta según la modalidad de la matrícula.
*   **Contabilidad Automática (Gastos):** El método `PlanillaEmpleado.save()` crea un registro de `Gasto` por el sueldo neto y lo atribuye a la sede a la que pertenece el empleado.
*   **Cálculo de Planilla:** La lógica reside en `EmpleadoForm.calcular_remuneracion()`. Calcula el sueldo neto y los aportes del empleador basándose en el sueldo básico, bonos, descuentos y la tasa de AFP configurable por empleado.
*   **Seguridad (RBAC):** Las vistas en `gestion/views.py` están protegidas por decoradores personalizados (`@require_permiso_personalizado`) que verifican los permisos del usuario antes de permitir el acceso.

## 4. Puntos a Mejorar (Deuda Técnica)

*   **Lógica de Negocio en Scripts:** La asignación de empleados a sedes es un script manual. Una mejora sería hacer esta regla configurable en el panel de admin (ej. un campo "Sede por defecto" en el modelo `RolEmpleado`).
*   **Precisión de Planilla:** El cálculo de planilla es una buena aproximación, pero para un uso en producción en Perú, necesita ser expandido para incluir el **Impuesto a la Renta de 5ta Categoría** y un modelo más detallado de las **comisiones de las AFP**.
*   **Uso de SQL Directo:** Algunas vistas complejas usan SQL directo. Se recomienda refactorizar estas consultas para usar el **ORM de Django** con `select_related` y `prefetch_related` para mejorar la mantenibilidad y seguridad.

## 5. Scripts de Utilidad

El directorio `gestion/scripts/` contiene scripts útiles para la administración:

*   **`crear_roles_iniciales.py`**: **(Recomendado)** Se debe ejecutar después de `migrate` en una base de datos limpia para crear los roles y permisos básicos necesarios para que la aplicación funcione correctamente.
*   **`asignar_empleados_sedes.py`**: Asigna masivamente los empleados a su sede correspondiente según las reglas hardcodeadas en el script.
*   **`verificar_permisos_rol.py`**: Script de debugging para verificar los permisos de un rol específico.
