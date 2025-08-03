# Generador de Reportes - Análisis de Datos

Este programa genera reportes de métricas web en formato LaTeX con una interfaz web moderna y fácil de usar.

## Características

- **Interfaz web**: Formulario HTML moderno con Bootstrap
- **Selección de fechas**: Calendario integrado para seleccionar días individuales o rangos
- **Dos tipos de reporte**:
  - Reporte de un día específico
  - Reporte de varios días (rango de fechas)
- **Vista previa**: Visualiza el código LaTeX antes de generar
- **Generación automática de PDF**: Descarga directa del archivo PDF
- **Responsive**: Funciona en desktop y móvil

## Instalación

1. Instala las dependencias de Python:
```bash
pip install -r requirements.txt
```

2. **IMPORTANTE**: Para generar PDFs, instala LaTeX:
   - **Ubuntu/Debian**: `sudo apt-get install texlive-full`
   - **macOS**: `brew install --cask mactex`
   - **Windows**: Descarga MiKTeX desde https://miktex.org/

## Uso

1. Ejecuta la aplicación web:
```bash
python app.py
```

2. Abre tu navegador y ve a: `http://localhost:5000`

2. **Selecciona el tipo de reporte**:
   - "Reporte de un día": Para métricas de una fecha específica
   - "Reporte de varios días": Para un rango de fechas

3. **Elige las fechas**:
   - Usa el calendario para seleccionar la fecha o rango de fechas

4. **Edita las métricas**:
   - Modifica los valores en los campos del formulario
   - Todos los campos son editables

5. **Añade observaciones**:
   - Escribe comentarios adicionales en el área de texto

6. **Genera el reporte**:
   - Haz clic en "Vista Previa" para ver el código LaTeX
   - Haz clic en "Generar Reporte" para crear los archivos

## Estructura del Reporte

El reporte incluye:
- Título con fecha(s) seleccionada(s)
- Tabla de métricas comparativas (mes actual vs anterior)
- Sección de observaciones personalizables

## Métricas Incluidas

- Visitas únicas
- Páginas más vistas
- Tiempo promedio en el sitio
- Clics al botón de WhatsApp
- Dispositivos más usados
- Problemas detectados
- Vendedora más seleccionada
- Test Vocacional
- Formulario

## Archivos Generados

Los reportes se guardan en la carpeta `reportes/`:
- `reporte_YYYY-MM-DD.tex` (un día)
- `reporte_YYYY-MM-DD_a_YYYY-MM-DD.tex` (varios días)
- Archivos PDF correspondientes (si LaTeX está instalado)

## Personalización

Puedes modificar:
- Plantilla LaTeX en la función `generar_latex()`
- Métricas disponibles en `crear_campos_metricas()`
- Datos de ejemplo en `cargar_datos_ejemplo()`