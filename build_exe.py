"""
Script para crear el ejecutable de Windows usando PyInstaller
"""
import os
import subprocess
import sys

def crear_ejecutable():
    """Crea el ejecutable usando PyInstaller"""
    
    # Comando PyInstaller (ajustado para Linux)
    comando = [
        'pyinstaller',
        '--onefile',                    # Un solo archivo ejecutable
        '--noconsole',                  # Sin ventana de consola
        '--add-data', 'templates:templates',  # Incluir templates (Linux usa :)
        '--name', 'GeneradorReportes',        # Nombre del ejecutable
        'app_desktop.py'
    ]
    
    # Si no tienes icono, remover esa línea
    if not os.path.exists('icon.ico'):
        comando = [cmd for cmd in comando if cmd != '--icon' and cmd != 'icon.ico']
    
    # Si no tienes carpeta static, remover esa línea
    if not os.path.exists('static'):
        comando = [cmd for cmd in comando if not cmd.startswith('static')]
    
    print("Creando ejecutable...")
    print("Comando:", ' '.join(comando))
    
    try:
        subprocess.run(comando, check=True)
        print("\n✅ Ejecutable creado exitosamente!")
        print("📁 Busca el archivo 'GeneradorReportes.exe' en la carpeta 'dist'")
        print("\n📋 Para distribuir a tus compañeros:")
        print("1. Copia el archivo GeneradorReportes.exe")
        print("2. Crea una carpeta 'reportes' donde esté el .exe")
        print("3. ¡Listo! Solo necesitan hacer doble clic en el .exe")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear el ejecutable: {e}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller no está instalado.")
        print("Instálalo con: pip install pyinstaller")
        return False
    
    return True

if __name__ == "__main__":
    crear_ejecutable()