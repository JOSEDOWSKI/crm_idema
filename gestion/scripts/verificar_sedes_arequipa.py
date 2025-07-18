#!/usr/bin/env python
"""
Script para verificar el estado actual de las sedes y sus programas
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

def mostrar_todas_las_sedes():
    """Mostrar todas las sedes del sistema"""
    print("🏢 SEDES DEL SISTEMA")
    print("=" * 60)
    
    sedes = Sede.objects.all().order_by('nombre')
    
    for sede in sedes:
        print(f"\n📍 {sede.nombre}")
        print(f"   Descripción: {sede.descripcion}")
        
        # Contar programas por tipo
        programas = ProgramaAcademico.objects.filter(sede=sede)
        carreras = programas.filter(tipo_programa='Carrera Técnica').count()
        especializaciones = programas.filter(tipo_programa='Especialización').count()
        cursos = programas.filter(tipo_programa='Curso').count()
        
        print(f"   Programas: {programas.count()} total")
        print(f"     - Carreras Técnicas: {carreras}")
        print(f"     - Especializaciones: {especializaciones}")
        print(f"     - Cursos: {cursos}")

def mostrar_programas_por_sede():
    """Mostrar detalle de programas por sede"""
    print("\n\n📚 DETALLE DE PROGRAMAS POR SEDE")
    print("=" * 60)
    
    sedes = Sede.objects.all().order_by('nombre')
    
    for sede in sedes:
        print(f"\n🏢 {sede.nombre}")
        print("-" * 40)
        
        programas = ProgramaAcademico.objects.filter(sede=sede).order_by('tipo_programa', 'nombre_programa')
        
        if programas.exists():
            for programa in programas:
                print(f"  • {programa.nombre_programa}")
                print(f"    - Tipo: {programa.get_tipo_programa_display()}")
                print(f"    - Duración: {programa.duracion_meses} meses")
                print(f"    - Matrícula: S/. {programa.precio_matricula}")
                print(f"    - Pensión Virtual: S/. {programa.precio_pension_virtual}")
                print(f"    - Pensión Presencial: S/. {programa.precio_pension_presencial}")
                if programa.precio_curso_unico > 0:
                    print(f"    - Curso Único: S/. {programa.precio_curso_unico}")
                print()
        else:
            print("  ⚠ No hay programas asignados")

def verificar_asignaciones_virtuales():
    """Verificar que todos los programas virtuales estén en Arequipa Virtual"""
    print("\n🔍 VERIFICACIÓN DE ASIGNACIONES VIRTUALES")
    print("=" * 60)
    
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        
        # Programas con precio virtual
        programas_con_precio_virtual = ProgramaAcademico.objects.filter(
            precio_pension_virtual__gt=0
        )
        
        # Programas virtuales asignados a Arequipa Virtual
        programas_en_arequipa_virtual = ProgramaAcademico.objects.filter(
            sede=sede_virtual
        )
        
        print(f"✓ Programas con precio virtual: {programas_con_precio_virtual.count()}")
        print(f"✓ Programas en Arequipa Virtual: {programas_en_arequipa_virtual.count()}")
        
        # Verificar que todos los programas con precio virtual estén en Arequipa Virtual
        programas_faltantes = programas_con_precio_virtual.exclude(sede=sede_virtual)
        
        if programas_faltantes.exists():
            print(f"\n⚠ ADVERTENCIA: {programas_faltantes.count()} programas con precio virtual NO están en Arequipa Virtual:")
            for programa in programas_faltantes:
                print(f"  • {programa.nombre_programa} - Sede actual: {programa.sede.nombre if programa.sede else 'Sin sede'}")
        else:
            print("\n✅ Todos los programas virtuales están correctamente asignados a Arequipa Virtual")
        
        # Verificar que no hay programas sin precio virtual en Arequipa Virtual
        programas_sin_precio_virtual = ProgramaAcademico.objects.filter(
            sede=sede_virtual,
            precio_pension_virtual=0
        )
        
        if programas_sin_precio_virtual.exists():
            print(f"\n⚠ ADVERTENCIA: {programas_sin_precio_virtual.count()} programas en Arequipa Virtual sin precio virtual:")
            for programa in programas_sin_precio_virtual:
                print(f"  • {programa.nombre_programa}")
        else:
            print("\n✅ Todos los programas en Arequipa Virtual tienen precio virtual")
            
    except Sede.DoesNotExist:
        print("✗ No se encontró la sede 'Arequipa Virtual'")

def mostrar_resumen_financiero():
    """Mostrar resumen financiero por sede"""
    print("\n💰 RESUMEN FINANCIERO POR SEDE")
    print("=" * 60)
    
    sedes = Sede.objects.all().order_by('nombre')
    
    for sede in sedes:
        print(f"\n🏢 {sede.nombre}")
        print("-" * 30)
        
        programas = ProgramaAcademico.objects.filter(sede=sede)
        
        if programas.exists():
            total_matriculas = sum(p.precio_matricula for p in programas)
            total_pensiones_virtual = sum(p.precio_pension_virtual * p.numero_pensiones for p in programas)
            total_pensiones_presencial = sum(p.precio_pension_presencial * p.numero_pensiones for p in programas)
            total_cursos_unicos = sum(p.precio_curso_unico for p in programas)
            
            print(f"  Total matrículas: S/. {total_matriculas:.2f}")
            print(f"  Total pensiones virtuales: S/. {total_pensiones_virtual:.2f}")
            print(f"  Total pensiones presenciales: S/. {total_pensiones_presencial:.2f}")
            print(f"  Total cursos únicos: S/. {total_cursos_unicos:.2f}")
            
            total_general = total_matriculas + total_pensiones_virtual + total_pensiones_presencial + total_cursos_unicos
            print(f"  💰 TOTAL GENERAL: S/. {total_general:.2f}")
        else:
            print("  ⚠ No hay programas asignados")

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DE SEDES")
    print("=" * 60)
    
    # Mostrar todas las sedes
    mostrar_todas_las_sedes()
    
    # Mostrar detalle de programas por sede
    mostrar_programas_por_sede()
    
    # Verificar asignaciones virtuales
    verificar_asignaciones_virtuales()
    
    # Mostrar resumen financiero
    mostrar_resumen_financiero()
    
    print("\n✅ Verificación completada")

if __name__ == '__main__':
    main() 