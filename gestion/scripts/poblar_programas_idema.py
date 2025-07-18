#!/usr/bin/env python
"""
Script para poblar la base de datos con los programas académicos del Instituto IDEMA
Basado en la información de: https://www.idema.edu.pe/#portfolio
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
from gestion.models import PermisoPersonalizado

PERMISOS = [
    ("dashboard", "Dashboard"),
    ("leads", "Leads"),
    ("crear_lead", "Crear Lead"),
    ("matriculas", "Matrículas"),
    ("malla_curricular", "Malla Curricular"),
    ("asistencia_presencial", "Asistencia Presencial"),
    ("empleados", "Empleados"),
    ("nuevo_empleado", "Nuevo empleado"),
    ("documentacion", "Documentación"),
    ("consulta_sql", "Consulta SQL"),
    ("tablas_bd", "Tablas BD"),
    ("poblar_bd", "Poblar BD"),
    ("finanzas", "Finanzas"),
]

def poblar_sedes_idema():
    """Poblar las sedes de IDEMA"""
    sedes = [
        ('Sede Principal Lima', 'Sede principal ubicada en Lima'),
        ('Campus Virtual IDEMA', 'Plataforma virtual de aprendizaje'),
    ]
    
    for nombre, descripcion in sedes:
        sede, created = Sede.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
        if created:
            print(f"✓ Sede creada: {nombre}")
        else:
            print(f"⚠ Sede ya existe: {nombre}")
    
    return Sede.objects.get(nombre='Sede Principal Lima')

def poblar_carreras_tecnicas():
    """Poblar las carreras técnicas de IDEMA (3 años)"""
    sede_principal = Sede.objects.get(nombre='Sede Principal Lima')
    
    carreras = [
        {
            'nombre_programa': 'Agropecuaria',
            'tipo_programa': 'Carrera Técnica',
            'duracion_meses': 36,
            'numero_pensiones': 36,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 250.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Enfermería',
            'tipo_programa': 'Carrera Técnica',
            'duracion_meses': 36,
            'numero_pensiones': 36,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 250.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Contabilidad',
            'tipo_programa': 'Carrera Técnica',
            'duracion_meses': 36,
            'numero_pensiones': 36,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 250.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Administración de Empresas',
            'tipo_programa': 'Carrera Técnica',
            'duracion_meses': 36,
            'numero_pensiones': 36,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 250.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Administración Bancaria',
            'tipo_programa': 'Carrera Técnica',
            'duracion_meses': 36,
            'numero_pensiones': 36,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 250.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        }
    ]
    
    for carrera in carreras:
        programa, created = ProgramaAcademico.objects.get_or_create(
            nombre_programa=carrera['nombre_programa'],
            defaults=carrera
        )
        if created:
            print(f"✓ Carrera creada: {carrera['nombre_programa']}")
        else:
            print(f"⚠ Carrera ya existe: {carrera['nombre_programa']}")

def poblar_especializaciones():
    """Poblar las especializaciones de IDEMA (1 año)"""
    sede_principal = Sede.objects.get(nombre='Sede Principal Lima')
    
    especializaciones = [
        {
            'nombre_programa': 'Veterinaria',
            'tipo_programa': 'Especialización',
            'duracion_meses': 12,
            'numero_pensiones': 12,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 200.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Farmacia',
            'tipo_programa': 'Especialización',
            'duracion_meses': 12,
            'numero_pensiones': 12,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 200.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Agronomía',
            'tipo_programa': 'Especialización',
            'duracion_meses': 12,
            'numero_pensiones': 12,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 200.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Psicología',
            'tipo_programa': 'Especialización',
            'duracion_meses': 12,
            'numero_pensiones': 12,
            'precio_matricula': 100.00,
            'precio_pension_virtual': 150.00,
            'precio_pension_presencial': 200.00,
            'precio_curso_unico': 0.00,
            'sede': sede_principal
        }
    ]
    
    for especializacion in especializaciones:
        programa, created = ProgramaAcademico.objects.get_or_create(
            nombre_programa=especializacion['nombre_programa'],
            defaults=especializacion
        )
        if created:
            print(f"✓ Especialización creada: {especializacion['nombre_programa']}")
        else:
            print(f"⚠ Especialización ya existe: {especializacion['nombre_programa']}")

def poblar_cursos():
    """Poblar los cursos de IDEMA (1 mes)"""
    sede_principal = Sede.objects.get(nombre='Sede Principal Lima')
    
    cursos = [
        {
            'nombre_programa': 'Atención Cliente Veterinario',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Fisioterapia y Rehabilitación',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Facturación Electrónica',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Administración de Empresas',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Contabilidad',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Enfermería',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Agropecuaria',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Psicología',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Farmacia',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        },
        {
            'nombre_programa': 'Veterinaria',
            'tipo_programa': 'Curso',
            'duracion_meses': 1,
            'numero_pensiones': 1,
            'precio_matricula': 0.00,
            'precio_pension_virtual': 0.00,
            'precio_pension_presencial': 0.00,
            'precio_curso_unico': 150.00,
            'sede': sede_principal
        }
    ]
    
    for curso in cursos:
        programa, created = ProgramaAcademico.objects.get_or_create(
            nombre_programa=curso['nombre_programa'],
            defaults=curso
        )
        if created:
            print(f"✓ Curso creado: {curso['nombre_programa']}")
        else:
            print(f"⚠ Curso ya existe: {curso['nombre_programa']}")

def poblar_modalidades():
    """Poblar las modalidades de estudio de IDEMA"""
    modalidades = [
        'Virtual',
        'Semi-presencial',
        'Presencial'
    ]
    
    for modalidad in modalidades:
        mod, created = Modalidad.objects.get_or_create(
            nombre_modalidad=modalidad
        )
        if created:
            print(f"✓ Modalidad creada: {modalidad}")
        else:
            print(f"⚠ Modalidad ya existe: {modalidad}")

def poblar_permisos():
    for codigo, nombre in PERMISOS:
        PermisoPersonalizado.objects.get_or_create(codigo=codigo, defaults={"nombre": nombre})
    print("Permisos personalizados poblados correctamente.")

def mostrar_estadisticas():
    """Mostrar estadísticas de los programas creados"""
    total_programas = ProgramaAcademico.objects.count()
    carreras = ProgramaAcademico.objects.filter(tipo_programa='Carrera Técnica').count()
    especializaciones = ProgramaAcademico.objects.filter(tipo_programa='Especialización').count()
    cursos = ProgramaAcademico.objects.filter(tipo_programa='Curso').count()
    
    print("\n📊 ESTADÍSTICAS DE PROGRAMAS IDEMA:")
    print("=" * 50)
    print(f"📚 Total de programas: {total_programas}")
    print(f"🎓 Carreras técnicas: {carreras}")
    print(f"📖 Especializaciones: {especializaciones}")
    print(f"📝 Cursos: {cursos}")
    print("=" * 50)

def main():
    """Función principal para poblar todos los programas de IDEMA"""
    print("🎓 Poblando programas académicos del Instituto IDEMA...")
    print("=" * 60)
    
    print("\n🏢 1. Poblando sedes...")
    poblar_sedes_idema()
    
    print("\n🎓 2. Poblando carreras técnicas...")
    poblar_carreras_tecnicas()
    
    print("\n📖 3. Poblando especializaciones...")
    poblar_especializaciones()
    
    print("\n📝 4. Poblando cursos...")
    poblar_cursos()
    
    print("\n🎯 5. Poblando modalidades...")
    poblar_modalidades()
    
    print("\n" + "=" * 60)
    print("✅ ¡Poblado de programas IDEMA completado!")
    
    mostrar_estadisticas()

if __name__ == '__main__':
    main() 