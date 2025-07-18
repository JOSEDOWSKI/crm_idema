#!/usr/bin/env python
"""
Script para verificar y mostrar estadísticas de la información geográfica del Perú
"""

import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from gestion.models import Departamento, Provincia, Distrito

def mostrar_estadisticas_generales():
    """Mostrar estadísticas generales de la información geográfica"""
    total_dept = Departamento.objects.count()
    total_prov = Provincia.objects.count()
    total_dist = Distrito.objects.count()
    
    print("🌍 ESTADÍSTICAS DE INFORMACIÓN GEOGRÁFICA DEL PERÚ")
    print("=" * 60)
    print(f"📋 Departamentos: {total_dept}")
    print(f"🏛️ Provincias: {total_prov}")
    print(f"🏘️ Distritos: {total_dist}")
    print("=" * 60)

def mostrar_departamentos():
    """Mostrar todos los departamentos"""
    print("\n📋 DEPARTAMENTOS DEL PERÚ:")
    print("-" * 40)
    
    departamentos = Departamento.objects.all().order_by('id_departamento')
    for dept in departamentos:
        provincias_count = Provincia.objects.filter(id_departamento=dept).count()
        print(f"{dept.id_departamento} - {dept.nombre} ({provincias_count} provincias)")

def mostrar_provincias_por_departamento():
    """Mostrar provincias por departamento"""
    print("\n🏛️ PROVINCIAS POR DEPARTAMENTO:")
    print("-" * 50)
    
    departamentos = Departamento.objects.all().order_by('id_departamento')
    for dept in departamentos:
        print(f"\n{dept.nombre.upper()}:")
        provincias = Provincia.objects.filter(id_departamento=dept).order_by('id_provincia')
        for prov in provincias:
            distritos_count = Distrito.objects.filter(id_provincia=prov).count()
            print(f"  • {prov.id_provincia} - {prov.nombre} ({distritos_count} distritos)")

def mostrar_distritos_principales():
    """Mostrar distritos de las principales ciudades"""
    print("\n🏘️ DISTRITOS DE PRINCIPALES CIUDADES:")
    print("-" * 50)
    
    ciudades_principales = [
        ('Lima', '1501'),
        ('Arequipa', '0401'),
        ('Trujillo', '1301'),
        ('Chiclayo', '1401'),
        ('Piura', '2001'),
    ]
    
    for ciudad, prov_id in ciudades_principales:
        try:
            provincia = Provincia.objects.get(id_provincia=prov_id)
            print(f"\n{ciudad.upper()}:")
            distritos = Distrito.objects.filter(id_provincia=provincia).order_by('id_distrito')
            for dist in distritos:
                print(f"  • {dist.id_distrito} - {dist.nombre}")
        except Provincia.DoesNotExist:
            print(f"\n{ciudad.upper()}: No encontrada")

def verificar_integridad():
    """Verificar la integridad de los datos geográficos"""
    print("\n🔍 VERIFICACIÓN DE INTEGRIDAD:")
    print("-" * 40)
    
    # Verificar que todos los departamentos tengan provincias
    dept_sin_prov = []
    for dept in Departamento.objects.all():
        if not Provincia.objects.filter(id_departamento=dept).exists():
            dept_sin_prov.append(dept.nombre)
    
    if dept_sin_prov:
        print(f"⚠ Departamentos sin provincias: {', '.join(dept_sin_prov)}")
    else:
        print("✓ Todos los departamentos tienen provincias")
    
    # Verificar que las provincias principales tengan distritos
    prov_sin_dist = []
    for prov in Provincia.objects.all():
        if not Distrito.objects.filter(id_provincia=prov).exists():
            prov_sin_dist.append(f"{prov.nombre} ({prov.id_departamento.nombre})")
    
    if prov_sin_dist:
        print(f"⚠ Provincias sin distritos: {len(prov_sin_dist)}")
        if len(prov_sin_dist) <= 10:
            for prov in prov_sin_dist:
                print(f"  • {prov}")
    else:
        print("✓ Todas las provincias tienen distritos")

def main():
    """Función principal"""
    mostrar_estadisticas_generales()
    mostrar_departamentos()
    mostrar_provincias_por_departamento()
    mostrar_distritos_principales()
    verificar_integridad()
    
    print("\n" + "=" * 60)
    print("✅ Verificación completada")

if __name__ == '__main__':
    main() 