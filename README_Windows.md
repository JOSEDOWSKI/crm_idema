# Generador de Reportes - Instalación para Windows

## Opción A: Crear ejecutable en Windows

### Requisitos:
- Python 3.8 o superior instalado en Windows
- Los archivos del proyecto

### Pasos:
1. Descargar e instalar Python desde python.org
2. Abrir Command Prompt (cmd) como administrador
3. Navegar a la carpeta del proyecto
4. Ejecutar los siguientes comandos:

```cmd
pip install -r requirements.txt
pip install pyinstaller
python build_exe_windows.py
```

5. El ejecutable estará en la carpeta `dist/GeneradorReportes.exe`

## Opción B: Ejecutar directamente con Python

### Pasos:
1. Instalar Python 3.8+
2. Abrir Command Prompt en la carpeta del proyecto
3. Ejecutar:
```cmd
pip install -r requirements.txt
python app_desktop.py
```

## Opción C: Usar la versión web
```cmd
pip install -r requirements.txt
python app.py
```
Luego abrir http://localhost:5001 en el navegador

## Estructura de archivos necesaria:
```
GeneradorReportes/
├── app_desktop.py
├── pdf_generator.py
├── requirements.txt
├── templates/
│   └── index.html
└── reportes/ (se crea automáticamente)
```