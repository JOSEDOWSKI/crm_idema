#!/usr/bin/env python
"""
Script para asignar empleados a sedes según su rol o función
"""

import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from gestion.models import Empleado, Sede, Usuario

def asignar_empleados_sedes():
    """Asignar empleados a sedes según su rol o función"""
    print("🔄 ASIGNANDO EMPLEADOS A SEDES")
    print("=" * 60)
    
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        sede_pedregal = Sede.objects.get(nombre='Sede Principal Pedregal')
    except Sede.DoesNotExist as e:
        print(f"✗ Error: {e}")
        return
    
    # Reglas de asignación por rol
    roles_virtual = ['Profesor', 'Estudiante']  # Roles que van a sede virtual
    roles_presencial = ['Admin', 'Ventas', 'Analista']  # Roles que van a sede presencial
    
    empleados_actualizados = 0
    empleados_virtual = 0
    empleados_presencial = 0
    
    # Procesar todos los empleados
    empleados = Empleado.objects.select_related('usuario__rol').all()
    
    for empleado in empleados:
        rol = empleado.usuario.rol.nombre if empleado.usuario and empleado.usuario.rol else None
        sede_anterior = empleado.sede
        
        # Determinar sede según rol
        if rol in roles_virtual:
            sede_nueva = sede_virtual
            empleados_virtual += 1
        elif rol in roles_presencial:
            sede_nueva = sede_pedregal
            empleados_presencial += 1
        else:
            # Para roles no definidos, usar sede presencial por defecto
            sede_nueva = sede_pedregal
            empleados_presencial += 1
        
        # Actualizar sede del empleado
        if empleado.sede != sede_nueva:
            empleado.sede = sede_nueva
            empleado.save(update_fields=['sede'])
            empleados_actualizados += 1
            print(f"✓ Empleado {empleado.nombres} {empleado.apellidos} asignado a {sede_nueva.nombre}")
    
    print(f"\n📊 RESUMEN DE ASIGNACIONES:")
    print(f"✓ Empleados actualizados: {empleados_actualizados}")
    print(f"✓ Empleados en Arequipa Virtual: {empleados_virtual}")
    print(f"✓ Empleados en Sede Principal Pedregal: {empleados_presencial}")

def verificar_asignaciones_empleados():
    """Verificar que las asignaciones se realizaron correctamente"""
    print("\n🔍 VERIFICACIÓN DE ASIGNACIONES DE EMPLEADOS")
    print("=" * 60)
    
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        sede_pedregal = Sede.objects.get(nombre='Sede Principal Pedregal')
        
        # Contar empleados por sede
        empleados_virtual = Empleado.objects.filter(sede=sede_virtual).count()
        empleados_pedregal = Empleado.objects.filter(sede=sede_pedregal).count()
        empleados_sin_sede = Empleado.objects.filter(sede__isnull=True).count()
        
        print(f"✓ Empleados en Arequipa Virtual: {empleados_virtual}")
        print(f"✓ Empleados en Sede Principal Pedregal: {empleados_pedregal}")
        print(f"⚠ Empleados sin sede asignada: {empleados_sin_sede}")
        
        # Mostrar empleados por sede
        print(f"\n📋 EMPLEADOS POR SEDE:")
        
        print(f"\n🏢 {sede_virtual.nombre}:")
        empleados_ejemplo_virtual = Empleado.objects.filter(sede=sede_virtual)[:5]
        for empleado in empleados_ejemplo_virtual:
            rol = empleado.usuario.rol.nombre if empleado.usuario and empleado.usuario.rol else 'Sin rol'
            print(f"  • {empleado.nombres} {empleado.apellidos} - {rol}")
        
        print(f"\n🏢 {sede_pedregal.nombre}:")
        empleados_ejemplo_pedregal = Empleado.objects.filter(sede=sede_pedregal)[:5]
        for empleado in empleados_ejemplo_pedregal:
            rol = empleado.usuario.rol.nombre if empleado.usuario and empleado.usuario.rol else 'Sin rol'
            print(f"  • {empleado.nombres} {empleado.apellidos} - {rol}")
        
        if empleados_sin_sede > 0:
            print(f"\n⚠ EMPLEADOS SIN SEDE ASIGNADA:")
            empleados_sin_sede_list = Empleado.objects.filter(sede__isnull=True)[:5]
            for empleado in empleados_sin_sede_list:
                rol = empleado.usuario.rol.nombre if empleado.usuario and empleado.usuario.rol else 'Sin rol'
                print(f"  • {empleado.nombres} {empleado.apellidos} - {rol}")
        
    except Sede.DoesNotExist as e:
        print(f"✗ Error: {e}")

def mostrar_resumen_nomina():
    """Mostrar resumen de nómina por sede"""
    print("\n💰 RESUMEN DE NÓMINA POR SEDE")
    print("=" * 60)
    
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        sede_pedregal = Sede.objects.get(nombre='Sede Principal Pedregal')
        
        # Calcular totales de nómina por sede
        empleados_virtual = Empleado.objects.filter(sede=sede_virtual)
        empleados_pedregal = Empleado.objects.filter(sede=sede_pedregal)
        
        total_nomina_virtual = sum(e.neto_mensual for e in empleados_virtual)
        total_nomina_pedregal = sum(e.neto_mensual for e in empleados_pedregal)
        total_aportes_virtual = sum(e.aporte_empleador for e in empleados_virtual)
        total_aportes_pedregal = sum(e.aporte_empleador for e in empleados_pedregal)
        
        print(f"\n🏢 {sede_virtual.nombre}:")
        print(f"  Empleados: {empleados_virtual.count()}")
        print(f"  Total nómina: S/. {total_nomina_virtual:.2f}")
        print(f"  Total aportes empleador: S/. {total_aportes_virtual:.2f}")
        print(f"  Costo total: S/. {total_nomina_virtual + total_aportes_virtual:.2f}")
        
        print(f"\n🏢 {sede_pedregal.nombre}:")
        print(f"  Empleados: {empleados_pedregal.count()}")
        print(f"  Total nómina: S/. {total_nomina_pedregal:.2f}")
        print(f"  Total aportes empleador: S/. {total_aportes_pedregal:.2f}")
        print(f"  Costo total: S/. {total_nomina_pedregal + total_aportes_pedregal:.2f}")
        
        print(f"\n💰 TOTAL GENERAL:")
        total_nomina = total_nomina_virtual + total_nomina_pedregal
        total_aportes = total_aportes_virtual + total_aportes_pedregal
        print(f"  Total nómina: S/. {total_nomina:.2f}")
        print(f"  Total aportes empleador: S/. {total_aportes:.2f}")
        print(f"  Costo total: S/. {total_nomina + total_aportes:.2f}")
        
    except Sede.DoesNotExist as e:
        print(f"✗ Error: {e}")

def main():
    """Función principal"""
    print("🔄 SISTEMA DE ASIGNACIÓN DE EMPLEADOS A SEDES")
    print("=" * 60)
    
    # Asignar empleados a sedes
    asignar_empleados_sedes()
    
    # Verificar asignaciones
    verificar_asignaciones_empleados()
    
    # Mostrar resumen de nómina
    mostrar_resumen_nomina()
    
    print("\n✅ Proceso completado exitosamente")
    print("\n📋 REGLAS DE ASIGNACIÓN:")
    print("• Profesores y Estudiantes → Arequipa Virtual")
    print("• Admin, Ventas, Analistas → Sede Principal Pedregal")
    print("• Los gastos de nómina se registrarán automáticamente en la sede correspondiente")

if __name__ == '__main__':
    main() 