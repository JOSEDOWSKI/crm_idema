#!/usr/bin/env python
"""
Script para verificar los permisos asignados a un rol específico.
"""

import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from gestion.models import RolEmpleado

def verificar_permisos(nombre_rol):
    """
    Busca un rol por su nombre y lista los permisos asociados.
    """
    print(f"🔍 Verificando permisos para el rol: '{nombre_rol}'")
    print("=" * 60)

    try:
        # Buscar el rol por su nombre (insensible a mayúsculas/minúsculas)
        rol = RolEmpleado.objects.get(nombre__iexact=nombre_rol)

        # Obtener todos los permisos asociados a este rol
        permisos = rol.permisos.all().order_by('nombre')

        if permisos.exists():
            print(f"✅ El rol '{rol.nombre}' tiene los siguientes {permisos.count()} permisos:")
            for permiso in permisos:
                print(f"  - {permiso.nombre} (código: '{permiso.codigo}')")
        else:
            print(f"⚠️ El rol '{rol.nombre}' existe, pero no tiene ningún permiso asignado.")

    except RolEmpleado.DoesNotExist:
        print(f"✗ Error: No se encontró ningún rol con el nombre '{nombre_rol}'.")
        print("  Roles disponibles en la base de datos:")
        roles_disponibles = RolEmpleado.objects.all()
        if roles_disponibles.exists():
            for r in roles_disponibles:
                print(f"  - {r.nombre}")
        else:
            print("  (No hay roles creados en la base de datos)")

def main():
    """
    Función principal para ejecutar la verificación.
    Puedes cambiar 'Ventas' por cualquier otro rol que quieras verificar.
    """
    rol_a_verificar = 'Ventas'
    verificar_permisos(rol_a_verificar)

if __name__ == '__main__':
    main()
