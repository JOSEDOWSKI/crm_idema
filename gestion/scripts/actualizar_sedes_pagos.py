#!/usr/bin/env python
"""
Script para actualizar las sedes de los pagos existentes según la modalidad
"""

import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from gestion.models import Pago, Sede, Ingreso
from django.db import models

def actualizar_sedes_pagos_existentes():
    """Actualizar las sedes de todos los pagos existentes según la modalidad"""
    print("🔄 ACTUALIZANDO SEDES DE PAGOS EXISTENTES")
    print("=" * 60)
    
    # Obtener las sedes
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        sede_pedregal = Sede.objects.get(nombre='Sede Principal Pedregal')
    except Sede.DoesNotExist as e:
        print(f"✗ Error: {e}")
        return
    
    # Contadores
    pagos_actualizados = 0
    pagos_virtual = 0
    pagos_presencial = 0
    ingresos_creados = 0
    
    # Procesar todos los pagos
    pagos = Pago.objects.select_related('id_matricula__id_modalidad', 'id_matricula__id_programa').all()
    
    for pago in pagos:
        modalidad = pago.id_matricula.id_modalidad.nombre_modalidad.lower()
        sede_anterior = pago.sede
        
        # Determinar sede según modalidad
        if 'virtual' in modalidad:
            sede_nueva = sede_virtual
            pagos_virtual += 1
        elif 'presencial' in modalidad or 'semi' in modalidad:
            sede_nueva = sede_pedregal
            pagos_presencial += 1
        else:
            # Para otros casos, usar la sede del programa
            sede_nueva = pago.id_matricula.id_programa.sede
        
        # Actualizar sede del pago
        if pago.sede != sede_nueva:
            pago.sede = sede_nueva
            pago.save(update_fields=['sede'])
            pagos_actualizados += 1
            
            # Crear ingreso automático si no existe
            concepto = f"{pago.get_concepto_display()} - {pago.id_matricula.id_programa.nombre_programa}"
            if pago.numero_cuota:
                concepto += f" (Cuota {pago.numero_cuota})"
            
            # Verificar si ya existe un ingreso para este pago
            ingreso_existente = Ingreso.objects.filter(
                concepto=concepto,
                monto=pago.monto,
                fecha=pago.fecha_pago.date(),
                sede=sede_nueva
            ).first()
            
            if not ingreso_existente:
                Ingreso.objects.create(
                    sede=sede_nueva,
                    concepto=concepto,
                    monto=pago.monto,
                    fecha=pago.fecha_pago.date()
                )
                ingresos_creados += 1
                print(f"✓ Ingreso creado: {concepto} - S/. {pago.monto} - {sede_nueva.nombre}")
    
    print(f"\n📊 RESUMEN DE ACTUALIZACIONES:")
    print(f"✓ Pagos actualizados: {pagos_actualizados}")
    print(f"✓ Pagos virtuales: {pagos_virtual}")
    print(f"✓ Pagos presenciales: {pagos_presencial}")
    print(f"✓ Ingresos creados: {ingresos_creados}")

def verificar_asignaciones():
    """Verificar que las asignaciones se realizaron correctamente"""
    print("\n🔍 VERIFICACIÓN DE ASIGNACIONES")
    print("=" * 60)
    
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        sede_pedregal = Sede.objects.get(nombre='Sede Principal Pedregal')
        
        # Contar pagos por sede
        pagos_virtual = Pago.objects.filter(sede=sede_virtual).count()
        pagos_pedregal = Pago.objects.filter(sede=sede_pedregal).count()
        pagos_sin_sede = Pago.objects.filter(sede__isnull=True).count()
        
        print(f"✓ Pagos en Arequipa Virtual: {pagos_virtual}")
        print(f"✓ Pagos en Sede Principal Pedregal: {pagos_pedregal}")
        print(f"⚠ Pagos sin sede asignada: {pagos_sin_sede}")
        
        # Verificar ingresos por sede
        ingresos_virtual = Ingreso.objects.filter(sede=sede_virtual).count()
        ingresos_pedregal = Ingreso.objects.filter(sede=sede_pedregal).count()
        
        print(f"\n💰 INGRESOS POR SEDE:")
        print(f"✓ Ingresos en Arequipa Virtual: {ingresos_virtual}")
        print(f"✓ Ingresos en Sede Principal Pedregal: {ingresos_pedregal}")
        
        # Mostrar algunos ejemplos
        print(f"\n📋 EJEMPLOS DE PAGOS POR SEDE:")
        
        print(f"\n🏢 {sede_virtual.nombre}:")
        pagos_ejemplo_virtual = Pago.objects.filter(sede=sede_virtual)[:3]
        for pago in pagos_ejemplo_virtual:
            print(f"  • {pago.get_concepto_display()} - {pago.id_matricula.id_programa.nombre_programa} - S/. {pago.monto}")
        
        print(f"\n🏢 {sede_pedregal.nombre}:")
        pagos_ejemplo_pedregal = Pago.objects.filter(sede=sede_pedregal)[:3]
        for pago in pagos_ejemplo_pedregal:
            print(f"  • {pago.get_concepto_display()} - {pago.id_matricula.id_programa.nombre_programa} - S/. {pago.monto}")
        
        if pagos_sin_sede > 0:
            print(f"\n⚠ PAGOS SIN SEDE ASIGNADA:")
            pagos_sin_sede_list = Pago.objects.filter(sede__isnull=True)[:5]
            for pago in pagos_sin_sede_list:
                print(f"  • {pago.get_concepto_display()} - {pago.id_matricula.id_programa.nombre_programa} - Modalidad: {pago.id_matricula.id_modalidad.nombre_modalidad}")
        
    except Sede.DoesNotExist as e:
        print(f"✗ Error: {e}")

def mostrar_resumen_financiero():
    """Mostrar resumen financiero por sede"""
    print("\n💰 RESUMEN FINANCIERO POR SEDE")
    print("=" * 60)
    
    try:
        sede_virtual = Sede.objects.get(nombre='Arequipa Virtual')
        sede_pedregal = Sede.objects.get(nombre='Sede Principal Pedregal')
        
        # Calcular totales de pagos por sede
        total_pagos_virtual = Pago.objects.filter(sede=sede_virtual).aggregate(
            total=models.Sum('monto')
        )['total'] or 0
        
        total_pagos_pedregal = Pago.objects.filter(sede=sede_pedregal).aggregate(
            total=models.Sum('monto')
        )['total'] or 0
        
        # Calcular totales de ingresos por sede
        total_ingresos_virtual = Ingreso.objects.filter(sede=sede_virtual).aggregate(
            total=models.Sum('monto')
        )['total'] or 0
        
        total_ingresos_pedregal = Ingreso.objects.filter(sede=sede_pedregal).aggregate(
            total=models.Sum('monto')
        )['total'] or 0
        
        print(f"\n🏢 {sede_virtual.nombre}:")
        print(f"  Total pagos: S/. {total_pagos_virtual:.2f}")
        print(f"  Total ingresos: S/. {total_ingresos_virtual:.2f}")
        
        print(f"\n🏢 {sede_pedregal.nombre}:")
        print(f"  Total pagos: S/. {total_pagos_pedregal:.2f}")
        print(f"  Total ingresos: S/. {total_ingresos_pedregal:.2f}")
        
        print(f"\n💰 TOTAL GENERAL:")
        print(f"  Total pagos: S/. {total_pagos_virtual + total_pagos_pedregal:.2f}")
        print(f"  Total ingresos: S/. {total_ingresos_virtual + total_ingresos_pedregal:.2f}")
        
    except Sede.DoesNotExist as e:
        print(f"✗ Error: {e}")

def main():
    """Función principal"""
    print("🔄 SISTEMA DE ASIGNACIÓN AUTOMÁTICA DE SEDES")
    print("=" * 60)
    
    # Actualizar pagos existentes
    actualizar_sedes_pagos_existentes()
    
    # Verificar asignaciones
    verificar_asignaciones()
    
    # Mostrar resumen financiero
    mostrar_resumen_financiero()
    
    print("\n✅ Proceso completado exitosamente")
    print("\n📋 NOTAS IMPORTANTES:")
    print("• Los nuevos pagos se asignarán automáticamente según la modalidad")
    print("• Los ingresos se crearán automáticamente al registrar pagos")
    print("• Virtual → Arequipa Virtual")
    print("• Presencial/Semi-presencial → Sede Principal Pedregal")

if __name__ == '__main__':
    main() 