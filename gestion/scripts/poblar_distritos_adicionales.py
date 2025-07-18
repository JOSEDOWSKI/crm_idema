#!/usr/bin/env python
"""
Script para poblar distritos adicionales de las principales ciudades del Perú
"""

import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from gestion.models import Provincia, Distrito

def poblar_distritos_lima():
    """Poblar distritos de la provincia de Lima"""
    try:
        provincia_lima = Provincia.objects.get(id_provincia='1501')
        
        distritos_lima = [
            ('150101', 'Lima', '1501'),
            ('150102', 'Ancón', '1501'),
            ('150103', 'Ate', '1501'),
            ('150104', 'Barranco', '1501'),
            ('150105', 'Breña', '1501'),
            ('150106', 'Carabayllo', '1501'),
            ('150107', 'Chaclacayo', '1501'),
            ('150108', 'Chorrillos', '1501'),
            ('150109', 'Cieneguilla', '1501'),
            ('150110', 'Comas', '1501'),
            ('150111', 'El Agustino', '1501'),
            ('150112', 'Independencia', '1501'),
            ('150113', 'Jesús María', '1501'),
            ('150114', 'La Molina', '1501'),
            ('150115', 'La Victoria', '1501'),
            ('150116', 'Lince', '1501'),
            ('150117', 'Los Olivos', '1501'),
            ('150118', 'Lurigancho', '1501'),
            ('150119', 'Lurín', '1501'),
            ('150120', 'Magdalena del Mar', '1501'),
            ('150121', 'Miraflores', '1501'),
            ('150122', 'Pachacámac', '1501'),
            ('150123', 'Pucusana', '1501'),
            ('150124', 'Pueblo Libre', '1501'),
            ('150125', 'Puente Piedra', '1501'),
            ('150126', 'Punta Hermosa', '1501'),
            ('150127', 'Punta Negra', '1501'),
            ('150128', 'Rímac', '1501'),
            ('150129', 'San Bartolo', '1501'),
            ('150130', 'San Borja', '1501'),
            ('150131', 'San Isidro', '1501'),
            ('150132', 'San Juan de Lurigancho', '1501'),
            ('150133', 'San Juan de Miraflores', '1501'),
            ('150134', 'San Luis', '1501'),
            ('150135', 'San Martín de Porres', '1501'),
            ('150136', 'San Miguel', '1501'),
            ('150137', 'Santa Anita', '1501'),
            ('150138', 'Santa María del Mar', '1501'),
            ('150139', 'Santa Rosa', '1501'),
            ('150140', 'Santiago de Surco', '1501'),
            ('150141', 'Surquillo', '1501'),
            ('150142', 'Villa El Salvador', '1501'),
            ('150143', 'Villa María del Triunfo', '1501'),
        ]
        
        for codigo, nombre, prov_id in distritos_lima:
            dist, created = Distrito.objects.get_or_create(
                id_distrito=codigo,
                defaults={
                    'nombre': nombre,
                    'id_provincia': provincia_lima
                }
            )
            if created:
                print(f"✓ Distrito creado: {nombre}")
            else:
                print(f"⚠ Distrito ya existe: {nombre}")
                
    except Provincia.DoesNotExist:
        print("✗ Error: Provincia de Lima no encontrada")

def poblar_distritos_arequipa():
    """Poblar distritos de la provincia de Arequipa"""
    try:
        provincia_arequipa = Provincia.objects.get(id_provincia='0401')
        
        distritos_arequipa = [
            ('040101', 'Arequipa', '0401'),
            ('040102', 'Alto Selva Alegre', '0401'),
            ('040103', 'Cayma', '0401'),
            ('040104', 'Cerro Colorado', '0401'),
            ('040105', 'Characato', '0401'),
            ('040106', 'Chiguata', '0401'),
            ('040107', 'Jacobo Hunter', '0401'),
            ('040108', 'La Joya', '0401'),
            ('040109', 'Mariano Melgar', '0401'),
            ('040110', 'Miraflores', '0401'),
            ('040111', 'Mollebaya', '0401'),
            ('040112', 'Paucarpata', '0401'),
            ('040113', 'Pocsi', '0401'),
            ('040114', 'Polobaya', '0401'),
            ('040115', 'Quequeña', '0401'),
            ('040116', 'Sabandía', '0401'),
            ('040117', 'Sachaca', '0401'),
            ('040118', 'San Juan de Siguas', '0401'),
            ('040119', 'San Juan de Tarucani', '0401'),
            ('040120', 'Santa Isabel de Siguas', '0401'),
            ('040121', 'Santa Rita de Siguas', '0401'),
            ('040122', 'Socabaya', '0401'),
            ('040123', 'Tiabaya', '0401'),
            ('040124', 'Uchumayo', '0401'),
            ('040125', 'Vitor', '0401'),
            ('040126', 'Yanahuara', '0401'),
            ('040127', 'Yarabamba', '0401'),
            ('040128', 'Yura', '0401'),
            ('040129', 'José Luis Bustamante y Rivero', '0401'),
        ]
        
        for codigo, nombre, prov_id in distritos_arequipa:
            dist, created = Distrito.objects.get_or_create(
                id_distrito=codigo,
                defaults={
                    'nombre': nombre,
                    'id_provincia': provincia_arequipa
                }
            )
            if created:
                print(f"✓ Distrito creado: {nombre}")
            else:
                print(f"⚠ Distrito ya existe: {nombre}")
                
    except Provincia.DoesNotExist:
        print("✗ Error: Provincia de Arequipa no encontrada")

def poblar_distritos_trujillo():
    """Poblar distritos de la provincia de Trujillo"""
    try:
        provincia_trujillo = Provincia.objects.get(id_provincia='1301')
        
        distritos_trujillo = [
            ('130101', 'Trujillo', '1301'),
            ('130102', 'El Porvenir', '1301'),
            ('130103', 'Florencia de Mora', '1301'),
            ('130104', 'Huanchaco', '1301'),
            ('130105', 'La Esperanza', '1301'),
            ('130106', 'Laredo', '1301'),
            ('130107', 'Moche', '1301'),
            ('130108', 'Poroto', '1301'),
            ('130109', 'Salaverry', '1301'),
            ('130110', 'Simbal', '1301'),
            ('130111', 'Victor Larco Herrera', '1301'),
        ]
        
        for codigo, nombre, prov_id in distritos_trujillo:
            dist, created = Distrito.objects.get_or_create(
                id_distrito=codigo,
                defaults={
                    'nombre': nombre,
                    'id_provincia': provincia_trujillo
                }
            )
            if created:
                print(f"✓ Distrito creado: {nombre}")
            else:
                print(f"⚠ Distrito ya existe: {nombre}")
                
    except Provincia.DoesNotExist:
        print("✗ Error: Provincia de Trujillo no encontrada")

def poblar_distritos_chiclayo():
    """Poblar distritos de la provincia de Chiclayo"""
    try:
        provincia_chiclayo = Provincia.objects.get(id_provincia='1401')
        
        distritos_chiclayo = [
            ('140101', 'Chiclayo', '1401'),
            ('140102', 'Chongoyape', '1401'),
            ('140103', 'Eten', '1401'),
            ('140104', 'Eten Puerto', '1401'),
            ('140105', 'José Leonardo Ortíz', '1401'),
            ('140106', 'La Victoria', '1401'),
            ('140107', 'Lagunas', '1401'),
            ('140108', 'Monsefú', '1401'),
            ('140109', 'Nueva Arica', '1401'),
            ('140110', 'Oyotún', '1401'),
            ('140111', 'Picsi', '1401'),
            ('140112', 'Pimentel', '1401'),
            ('140113', 'Reque', '1401'),
            ('140114', 'Santa Rosa', '1401'),
            ('140115', 'Saña', '1401'),
            ('140116', 'Cayaltí', '1401'),
            ('140117', 'Patapo', '1401'),
            ('140118', 'Pomalca', '1401'),
            ('140119', 'Pucalá', '1401'),
            ('140120', 'Tumán', '1401'),
        ]
        
        for codigo, nombre, prov_id in distritos_chiclayo:
            dist, created = Distrito.objects.get_or_create(
                id_distrito=codigo,
                defaults={
                    'nombre': nombre,
                    'id_provincia': provincia_chiclayo
                }
            )
            if created:
                print(f"✓ Distrito creado: {nombre}")
            else:
                print(f"⚠ Distrito ya existe: {nombre}")
                
    except Provincia.DoesNotExist:
        print("✗ Error: Provincia de Chiclayo no encontrada")

def poblar_distritos_piura():
    """Poblar distritos de la provincia de Piura"""
    try:
        provincia_piura = Provincia.objects.get(id_provincia='2001')
        
        distritos_piura = [
            ('200101', 'Piura', '2001'),
            ('200102', 'Castilla', '2001'),
            ('200103', 'Catacaos', '2001'),
            ('200104', 'Cura Mori', '2001'),
            ('200105', 'El Tallán', '2001'),
            ('200106', 'La Arena', '2001'),
            ('200107', 'La Unión', '2001'),
            ('200108', 'Las Lomas', '2001'),
            ('200109', 'Tambo Grande', '2001'),
            ('200110', 'Veintiséis de Octubre', '2001'),
        ]
        
        for codigo, nombre, prov_id in distritos_piura:
            dist, created = Distrito.objects.get_or_create(
                id_distrito=codigo,
                defaults={
                    'nombre': nombre,
                    'id_provincia': provincia_piura
                }
            )
            if created:
                print(f"✓ Distrito creado: {nombre}")
            else:
                print(f"⚠ Distrito ya existe: {nombre}")
                
    except Provincia.DoesNotExist:
        print("✗ Error: Provincia de Piura no encontrada")

def main():
    """Función principal para poblar distritos adicionales"""
    print("🏘️ Poblando distritos adicionales de principales ciudades...")
    print("=" * 60)
    
    print("\n🏙️ 1. Poblando distritos de Lima...")
    poblar_distritos_lima()
    
    print("\n🏔️ 2. Poblando distritos de Arequipa...")
    poblar_distritos_arequipa()
    
    print("\n🏛️ 3. Poblando distritos de Trujillo...")
    poblar_distritos_trujillo()
    
    print("\n🌴 4. Poblando distritos de Chiclayo...")
    poblar_distritos_chiclayo()
    
    print("\n🌞 5. Poblando distritos de Piura...")
    poblar_distritos_piura()
    
    print("\n" + "=" * 60)
    print("✅ ¡Poblado de distritos adicionales completado!")
    
    # Mostrar estadísticas finales
    total_dist = Distrito.objects.count()
    print(f"\n📊 Total de distritos en la base de datos: {total_dist}")

if __name__ == '__main__':
    main() 