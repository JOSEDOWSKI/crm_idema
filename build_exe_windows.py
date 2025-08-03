"""
Script para crear el ejecutable de Windows usando PyInstaller
EJECUTAR ESTE ARCHIVO EN WINDOWS
"""
import os
import subprocess
import sys

def crear_ejecutable():
    """Crea el ejecutable usando PyInstaller en Windows"""
    
    print("=== CREADOR DE EJECUTABLE PARA WINDOWS ===")
    print("Verificando dependencias...")
    
    # Verificar que PyInstaller esté instalado
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("❌ PyInstaller no encontrado. Instalando...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Comando PyInstaller para Windows
    comando = [
        'pyinstaller',
        '--onefile',                           # Un solo archivo ejecutable
        '--noconsole',                         # Sin ventana de consola
        '--add-data', 'templates;templates',   # Incluir templates (Windows usa ;)
        '--name', 'GeneradorReportes',         # Nombre del ejecutable
        '--distpath', 'dist',                  # Carpeta de salida
        '--workpath', 'build',                 # Carpeta de trabajo
        'app_desktop.py'
    ]
    
    print("Creando ejecutable...")
    print("Esto puede tomar varios minutos...")
    
    try:
        # Ejecutar PyInstaller
        result = subprocess.run(comando, check=True, capture_output=True, text=True)
        
        print("\n✅ ¡Ejecutable creado exitosamente!")
        print("📁 Archivo creado: dist/GeneradorReportes.exe")
        print("\n📋 Para distribuir:")
        print("1. Copia GeneradorReportes.exe a cualquier PC Windows")
        print("2. Haz doble clic para ejecutar")
        print("3. Se abrirá automáticamente en el navegador")
        print("4. Los reportes se guardarán en una carpeta 'reportes' junto al .exe")
        
        # Crear carpeta reportes si no existe
        if not os.path.exists('dist/reportes'):
            os.makedirs('dist/reportes')
            print("✅ Carpeta 'reportes' creada en dist/")
        
        print("\n🎉 ¡Listo para usar!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear el ejecutable:")
        print(f"Salida: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if os.name != 'nt':
        print("⚠️  Este script debe ejecutarse en Windows")
        print("Sistema detectado:", os.name)
        input("Presiona Enter para continuar de todos modos...")
    
    crear_ejecutable()
    input("\nPresiona Enter para cerrar...")