#!/usr/bin/env python
"""
Script para verificar y mostrar todos los programas académicos de IDEMA en la base de datos
"""

import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from gestion.models import ProgramaAcademico, Sede, Modalidad

def mostrar_estadisticas_generales():
    """Mostrar estadísticas generales de los programas"""
    total_programas = ProgramaAcademico.objects.count()
    carreras = ProgramaAcademico.objects.filter(tipo_programa='Carrera Técnica').count()
    especializaciones = ProgramaAcademico.objects.filter(tipo_programa='Especialización').count()
    cursos = ProgramaAcademico.objects.filter(tipo_programa='Curso').count()
    
    print("🎓 ESTADÍSTICAS DE PROGRAMAS ACADÉMICOS IDEMA")
    print("=" * 60)
    print(f"📚 Total de programas: {total_programas}")
    print(f"🎓 Carreras técnicas: {carreras}")
    print(f"📖 Especializaciones: {especializaciones}")
    print(f"📝 Cursos: {cursos}")
    print("=" * 60)

def mostrar_carreras_tecnicas():
    """Mostrar todas las carreras técnicas"""
    print("\n🎓 CARRERAS TÉCNICAS (3 años):")
    print("-" * 50)
    
    carreras = ProgramaAcademico.objects.filter(tipo_programa='Carrera Técnica').order_by('nombre_programa')
    for carrera in carreras:
        print(f"• {carrera.nombre_programa}")
        print(f"  - Duración: {carrera.duracion_meses} meses")
        print(f"  - Pensiones: {carrera.numero_pensiones}")
        print(f"  - Matrícula: S/. {carrera.precio_matricula}")
        print(f"  - Pensión Virtual: S/. {carrera.precio_pension_virtual}")
        print(f"  - Pensión Presencial: S/. {carrera.precio_pension_presencial}")
        print(f"  - Sede: {carrera.sede.nombre if carrera.sede else 'No asignada'}")
        print()

def mostrar_especializaciones():
    """Mostrar todas las especializaciones"""
    print("\n📖 ESPECIALIZACIONES (1 año):")
    print("-" * 50)
    
    especializaciones = ProgramaAcademico.objects.filter(tipo_programa='Especialización').order_by('nombre_programa')
    for especializacion in especializaciones:
        print(f"• {especializacion.nombre_programa}")
        print(f"  - Duración: {especializacion.duracion_meses} meses")
        print(f"  - Pensiones: {especializacion.numero_pensiones}")
        print(f"  - Matrícula: S/. {especializacion.precio_matricula}")
        print(f"  - Pensión Virtual: S/. {especializacion.precio_pension_virtual}")
        print(f"  - Pensión Presencial: S/. {especializacion.precio_pension_presencial}")
        print(f"  - Sede: {especializacion.sede.nombre if especializacion.sede else 'No asignada'}")
        print()

def mostrar_cursos():
    """Mostrar todos los cursos"""
    print("\n📝 CURSOS (1 mes):")
    print("-" * 50)
    
    cursos = ProgramaAcademico.objects.filter(tipo_programa='Curso').order_by('nombre_programa')
    for curso in cursos:
        print(f"• {curso.nombre_programa}")
        print(f"  - Duración: {curso.duracion_meses} mes")
        print(f"  - Pensiones: {curso.numero_pensiones}")
        print(f"  - Precio único: S/. {curso.precio_curso_unico}")
        print(f"  - Sede: {curso.sede.nombre if curso.sede else 'No asignada'}")
        print()

def mostrar_sedes():
    """Mostrar las sedes disponibles"""
    print("\n🏢 SEDES DISPONIBLES:")
    print("-" * 30)
    
    sedes = Sede.objects.all().order_by('nombre')
    for sede in sedes:
        programas_count = ProgramaAcademico.objects.filter(sede=sede).count()
        print(f"• {sede.nombre}")
        print(f"  - Descripción: {sede.descripcion}")
        print(f"  - Programas: {programas_count}")
        print()

def mostrar_modalidades():
    """Mostrar las modalidades disponibles"""
    print("\n🎯 MODALIDADES DISPONIBLES:")
    print("-" * 35)
    
    modalidades = Modalidad.objects.all().order_by('nombre_modalidad')
    for modalidad in modalidades:
        print(f"• {modalidad.nombre_modalidad}")

def mostrar_programas_por_sede():
    """Mostrar programas agrupados por sede"""
    print("\n📊 PROGRAMAS POR SEDE:")
    print("-" * 40)
    
    sedes = Sede.objects.all().order_by('nombre')
    for sede in sedes:
        programas = ProgramaAcademico.objects.filter(sede=sede).order_by('tipo_programa', 'nombre_programa')
        if programas.exists():
            print(f"\n🏢 {sede.nombre}:")
            for programa in programas:
                print(f"  • {programa.nombre_programa} ({programa.get_tipo_programa_display()})")

def main():
    """Función principal"""
    mostrar_estadisticas_generales()
    mostrar_carreras_tecnicas()
    mostrar_especializaciones()
    mostrar_cursos()
    mostrar_sedes()
    mostrar_modalidades()
    mostrar_programas_por_sede()
    
    print("\n" + "=" * 60)
    print("✅ Verificación de programas IDEMA completada")

if __name__ == '__main__':
    main() 