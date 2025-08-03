@echo off
echo =================================
echo   GENERADOR DE REPORTES
echo =================================
echo.
echo Verificando Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python desde: https://python.org
    echo.
    pause
    exit /b 1
)

echo Python encontrado!
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Iniciando aplicacion...
echo La aplicacion se abrira automaticamente en tu navegador
echo Para cerrar, cierra esta ventana
echo.

python app_desktop.py

pause