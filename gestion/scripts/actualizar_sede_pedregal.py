#!/usr/bin/env python
"""
Script para actualizar la sede principal a "Sede Principal Pedregal"
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

def actualizar_sede_principal():
    """Actualizar la sede principal a Pedregal"""
    try:
        # Buscar la sede actual
        sede_actual = Sede.objects.get(nombre='Sede Principal Lima')
        
        # Actualizar nombre y descripción
        sede_actual.nombre = 'Sede Principal Pedregal'
        sede_actual.descripcion = 'Sede principal ubicada en Pedregal, Lima'
        sede_actual.save()
        
        print(f"✓ Sede actualizada: {sede_actual.nombre}")
        print(f"  - Nueva descripción: {sede_actual.descripcion}")
        
        # Contar programas asociados
        programas_count = ProgramaAcademico.objects.filter(sede=sede_actual).count()
        print(f"  - Programas asociados: {programas_count}")
        
        return sede_actual
        
    except Sede.DoesNotExist:
        print("✗ No se encontró la sede 'Sede Principal Lima'")
        return None

def mostrar_programas_sede():
    """Mostrar todos los programas de la sede Pedregal"""
    try:
        sede_pedregal = Sede.objects.get(nombre='Sede Principal Pedregal')
        
        print(f"\n📚 PROGRAMAS EN SEDE PEDREGAL:")
        print("-" * 50)
        
        programas = ProgramaAcademico.objects.filter(sede=sede_pedregal).order_by('tipo_programa', 'nombre_programa')
        
        if programas.exists():
            for programa in programas:
                print(f"• {programa.nombre_programa} ({programa.get_tipo_programa_display()})")
        else:
            print("No hay programas asignados a esta sede")
            
    except Sede.DoesNotExist:
        print("✗ No se encontró la sede 'Sede Principal Pedregal'")

def mostrar_estadisticas_sedes():
    """Mostrar estadísticas de todas las sedes"""
    print(f"\n🏢 ESTADÍSTICAS DE SEDES:")
    print("-" * 40)
    
    sedes = Sede.objects.all().order_by('nombre')
    for sede in sedes:
        programas_count = ProgramaAcademico.objects.filter(sede=sede).count()
        print(f"• {sede.nombre}")
        print(f"  - Descripción: {sede.descripcion}")
        print(f"  - Programas: {programas_count}")
        print()

def main():
    """Función principal"""
    print("🏢 Actualizando sede principal a Pedregal...")
    print("=" * 50)
    
    # Actualizar la sede
    sede_actualizada = actualizar_sede_principal()
    
    if sede_actualizada:
        # Mostrar programas de la sede
        mostrar_programas_sede()
        
        # Mostrar estadísticas generales
        mostrar_estadisticas_sedes()
        
        print("=" * 50)
        print("✅ ¡Actualización completada!")
    else:
        print("❌ No se pudo completar la actualización")

if __name__ == '__main__':
    main() 