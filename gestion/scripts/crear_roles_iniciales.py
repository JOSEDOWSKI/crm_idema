#!/usr/bin/env python
"""
Script para crear los roles y permisos iniciales en la base de datos.
Esto es necesario después de crear una base de datos limpia.
"""

import os
import sys
import django

# Configuración de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from gestion.models import RolEmpleado, PermisoPersonalizado

def crear_permisos_y_roles():
    """
    Crea los permisos y roles básicos del sistema.
    """
    print("🚀 Creando permisos y roles iniciales...")
    print("=" * 60)

    # --- 1. Crear todos los permisos personalizados ---
    print("Creando permisos...")
    permisos_data = PermisoPersonalizado.CODIGO_VISTA_CHOICES
    permisos_creados = 0
    for codigo, nombre in permisos_data:
        permiso, created = PermisoPersonalizado.objects.get_or_create(
            codigo=codigo,
            defaults={'nombre': nombre}
        )
        if created:
            permisos_creados += 1
            print(f"  - Permiso '{nombre}' creado.")
    print(f"✅ {permisos_creados} permisos nuevos creados.\n")

    # --- 2. Crear los roles básicos ---
    print("Creando roles...")
    roles_data = [
        "Admin",
        "Ventas",
        "Profesor",
        "Estudiante",
        "Analista"
    ]
    roles_creados = 0
    for nombre_rol in roles_data:
        rol, created = RolEmpleado.objects.get_or_create(nombre=nombre_rol)
        if created:
            roles_creados += 1
            print(f"  - Rol '{nombre_rol}' creado.")
    print(f"✅ {roles_creados} roles nuevos creados.\n")

    # --- 3. Asignar permisos a los roles ---
    print("Asignando permisos a los roles...")

    # Permisos para el rol de Ventas
    try:
        rol_ventas = RolEmpleado.objects.get(nombre='Ventas')
        permisos_ventas_codigos = [
            'dashboard',
            'leads',
            'crear_lead',
            'matriculas'
        ]
        permisos_ventas = PermisoPersonalizado.objects.filter(codigo__in=permisos_ventas_codigos)
        rol_ventas.permisos.set(permisos_ventas)
        print(f"✅ Permisos asignados al rol 'Ventas': {', '.join(p.nombre for p in permisos_ventas)}")
    except RolEmpleado.DoesNotExist:
        print("⚠️ No se encontró el rol 'Ventas' para asignarle permisos.")

    # Permisos para el rol de Admin (acceso a casi todo)
    try:
        rol_admin = RolEmpleado.objects.get(nombre='Admin')
        permisos_admin = PermisoPersonalizado.objects.all()
        rol_admin.permisos.set(permisos_admin)
        print(f"✅ Todos los {permisos_admin.count()} permisos asignados al rol 'Admin'.")
    except RolEmpleado.DoesNotExist:
        print("⚠️ No se encontró el rol 'Admin' para asignarle permisos.")

    print("\n🎉 Proceso de seeding completado.")

if __name__ == '__main__':
    crear_permisos_y_roles()
