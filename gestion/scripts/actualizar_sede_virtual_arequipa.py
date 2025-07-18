#!/usr/bin/env python
"""
Script para actualizar la sede virtual y asignar todos los programas virtuales a Arequipa Virtual
"""

import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from gestion.models import Sede, ProgramaAcademico

def actualizar_sede_virtual():
    """Actualizar la sede virtual para que sea Arequipa Virtual"""
    try:
        # Buscar la sede virtual existente
        sede_virtual = Sede.objects.get(nombre='Campus Virtual IDEMA')
        
        # Actualizar nombre y descripción
        sede_virtual.nombre = 'Arequipa Virtual'
        sede_virtual.descripcion = 'Sede virtual ubicada en Arequipa para programas a distancia'
        sede_virtual.save()
        
        print("✓ Sede virtual actualizada: 'Arequipa Virtual'")
        return sede_virtual
        
    except Sede.DoesNotExist:
        # Si no existe, crear la nueva sede
        sede_virtual = Sede.objects.create(
            nombre='Arequipa Virtual',
            descripcion='Sede virtual ubicada en Arequipa para programas a distancia'
        )
        print("✓ Nueva sede virtual creada: 'Arequipa Virtual'")
        return sede_virtual

def asignar_programas_virtuales():
    """Asignar todos los programas virtuales a la sede de Arequipa Virtual"""
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        
        # Obtener todos los programas que tienen precio_pension_virtual > 0
        programas_virtuales = ProgramaAcademico.objects.filter(
            precio_pension_virtual__gt=0
        )
        
        # Asignar la sede virtual a estos programas
        for programa in programas_virtuales:
            programa.sede = sede_virtual
            programa.save()
        
        print(f"✓ {programas_virtuales.count()} programas asignados a Arequipa Virtual")
        
        # Mostrar los programas asignados
        print("\n📋 Programas asignados a Arequipa Virtual:")
        for programa in programas_virtuales:
            print(f"  • {programa.nombre_programa} - {programa.get_tipo_programa_display()}")
        
    except Sede.DoesNotExist:
        print("✗ No se encontró la sede 'Arequipa Virtual'")

def verificar_asignaciones():
    """Verificar que las asignaciones se realizaron correctamente"""
    print("\n🔍 VERIFICACIÓN DE ASIGNACIONES:")
    print("-" * 50)
    
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        programas_asignados = ProgramaAcademico.objects.filter(sede=sede_virtual)
        
        print(f"✓ Sede: {sede_virtual.nombre}")
        print(f"✓ Descripción: {sede_virtual.descripcion}")
        print(f"✓ Programas asignados: {programas_asignados.count()}")
        
        if programas_asignados.exists():
            print("\n📚 Programas en Arequipa Virtual:")
            for programa in programas_asignados:
                print(f"  • {programa.nombre_programa} - {programa.get_tipo_programa_display()}")
                print(f"    - Pensión Virtual: S/. {programa.precio_pension_virtual}")
        
        # Verificar que no hay programas con precio virtual sin asignar
        programas_sin_asignar = ProgramaAcademico.objects.filter(
            precio_pension_virtual__gt=0,
            sede__isnull=True
        )
        
        if programas_sin_asignar.exists():
            print(f"\n⚠ ADVERTENCIA: {programas_sin_asignar.count()} programas con precio virtual sin sede asignada:")
            for programa in programas_sin_asignar:
                print(f"  • {programa.nombre_programa}")
        else:
            print("\n✓ Todos los programas virtuales están correctamente asignados")
            
    except Sede.DoesNotExist:
        print("✗ No se encontró la sede 'Arequipa Virtual'")

def main():
    """Función principal"""
    print("🔄 ACTUALIZANDO SEDE VIRTUAL A AREQUIPA")
    print("=" * 50)
    
    # Actualizar la sede virtual
    actualizar_sede_virtual()
    
    # Asignar programas virtuales
    asignar_programas_virtuales()
    
    # Verificar asignaciones
    verificar_asignaciones()
    
    print("\n✅ Proceso completado exitosamente")

if __name__ == '__main__':
    main() 