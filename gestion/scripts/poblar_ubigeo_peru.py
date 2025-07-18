#!/usr/bin/env python
"""
Script para poblar la base de datos con todos los departamentos y provincias del Perú
Basado en la información de Wikipedia: https://es.wikipedia.org/wiki/Portal:Per%C3%BA/Departamentos_y_provincias
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

def poblar_departamentos():
    """Poblar todos los departamentos del Perú"""
    departamentos = [
        ('01', 'Amazonas'),
        ('02', 'Áncash'),
        ('03', 'Apurímac'),
        ('04', 'Arequipa'),
        ('05', 'Ayacucho'),
        ('06', 'Cajamarca'),
        ('07', 'Callao'),
        ('08', 'Cusco'),
        ('09', 'Huancavelica'),
        ('10', 'Huánuco'),
        ('11', 'Ica'),
        ('12', 'Junín'),
        ('13', 'La Libertad'),
        ('14', 'Lambayeque'),
        ('15', 'Lima'),
        ('16', 'Loreto'),
        ('17', 'Madre de Dios'),
        ('18', 'Moquegua'),
        ('19', 'Pasco'),
        ('20', 'Piura'),
        ('21', 'Puno'),
        ('22', 'San Martín'),
        ('23', 'Tacna'),
        ('24', 'Tumbes'),
        ('25', 'Ucayali'),
    ]
    
    for codigo, nombre in departamentos:
        dept, created = Departamento.objects.get_or_create(
            id_departamento=codigo,
            defaults={'nombre': nombre}
        )
        if created:
            print(f"✓ Departamento creado: {nombre}")
        else:
            print(f"⚠ Departamento ya existe: {nombre}")

def poblar_provincias():
    """Poblar todas las provincias del Perú"""
    provincias = [
        # Amazonas (01)
        ('0101', 'Chachapoyas', '01'),
        ('0102', 'Bagua', '01'),
        ('0103', 'Bongará', '01'),
        ('0104', 'Condorcanqui', '01'),
        ('0105', 'Luya', '01'),
        ('0106', 'Rodríguez de Mendoza', '01'),
        ('0107', 'Utcubamba', '01'),
        
        # Áncash (02)
        ('0201', 'Huaraz', '02'),
        ('0202', 'Aija', '02'),
        ('0203', 'Antonio Raymondi', '02'),
        ('0204', 'Asunción', '02'),
        ('0205', 'Bolognesi', '02'),
        ('0206', 'Carhuaz', '02'),
        ('0207', 'Carlos Fermín Fitzcarrald', '02'),
        ('0208', 'Casma', '02'),
        ('0209', 'Corongo', '02'),
        ('0210', 'Huari', '02'),
        ('0211', 'Huarmey', '02'),
        ('0212', 'Huaylas', '02'),
        ('0213', 'Mariscal Luzuriaga', '02'),
        ('0214', 'Ocros', '02'),
        ('0215', 'Pallasca', '02'),
        ('0216', 'Pomabamba', '02'),
        ('0217', 'Recuay', '02'),
        ('0218', 'Santa', '02'),
        ('0219', 'Sihuas', '02'),
        ('0220', 'Yungay', '02'),
        
        # Apurímac (03)
        ('0301', 'Abancay', '03'),
        ('0302', 'Andahuaylas', '03'),
        ('0303', 'Antabamba', '03'),
        ('0304', 'Aymaraes', '03'),
        ('0305', 'Cotabambas', '03'),
        ('0306', 'Chincheros', '03'),
        ('0307', 'Grau', '03'),
        
        # Arequipa (04)
        ('0401', 'Arequipa', '04'),
        ('0402', 'Camaná', '04'),
        ('0403', 'Caravelí', '04'),
        ('0404', 'Castilla', '04'),
        ('0405', 'Caylloma', '04'),
        ('0406', 'Condesuyos', '04'),
        ('0407', 'Islay', '04'),
        ('0408', 'La Unión', '04'),
        
        # Ayacucho (05)
        ('0501', 'Huamanga', '05'),
        ('0502', 'Cangallo', '05'),
        ('0503', 'Huanca Sancos', '05'),
        ('0504', 'Huanta', '05'),
        ('0505', 'La Mar', '05'),
        ('0506', 'Lucanas', '05'),
        ('0507', 'Parinacochas', '05'),
        ('0508', 'Páucar del Sara Sara', '05'),
        ('0509', 'Sucre', '05'),
        ('0510', 'Víctor Fajardo', '05'),
        ('0511', 'Vilcas Huamán', '05'),
        
        # Cajamarca (06)
        ('0601', 'Cajamarca', '06'),
        ('0602', 'Cajabamba', '06'),
        ('0603', 'Celendín', '06'),
        ('0604', 'Chota', '06'),
        ('0605', 'Contumazá', '06'),
        ('0606', 'Cutervo', '06'),
        ('0607', 'Hualgayoc', '06'),
        ('0608', 'Jaén', '06'),
        ('0609', 'San Ignacio', '06'),
        ('0610', 'San Marcos', '06'),
        ('0611', 'San Miguel', '06'),
        ('0612', 'San Pablo', '06'),
        ('0613', 'Santa Cruz', '06'),
        
        # Callao (07)
        ('0701', 'Callao', '07'),
        
        # Cusco (08)
        ('0801', 'Cusco', '08'),
        ('0802', 'Acomayo', '08'),
        ('0803', 'Anta', '08'),
        ('0804', 'Calca', '08'),
        ('0805', 'Canas', '08'),
        ('0806', 'Canchis', '08'),
        ('0807', 'Chumbivilcas', '08'),
        ('0808', 'Espinar', '08'),
        ('0809', 'La Convención', '08'),
        ('0810', 'Paruro', '08'),
        ('0811', 'Paucartambo', '08'),
        ('0812', 'Quispicanchi', '08'),
        ('0813', 'Urubamba', '08'),
        
        # Huancavelica (09)
        ('0901', 'Huancavelica', '09'),
        ('0902', 'Acobamba', '09'),
        ('0903', 'Angaraes', '09'),
        ('0904', 'Castrovirreyna', '09'),
        ('0905', 'Churcampa', '09'),
        ('0906', 'Huaytará', '09'),
        ('0907', 'Tayacaja', '09'),
        
        # Huánuco (10)
        ('1001', 'Huánuco', '10'),
        ('1002', 'Ambo', '10'),
        ('1003', 'Dos de Mayo', '10'),
        ('1004', 'Huacaybamba', '10'),
        ('1005', 'Huamalíes', '10'),
        ('1006', 'Leoncio Prado', '10'),
        ('1007', 'Marañón', '10'),
        ('1008', 'Pachitea', '10'),
        ('1009', 'Puerto Inca', '10'),
        ('1010', 'Lauricocha', '10'),
        ('1011', 'Yarowilca', '10'),
        
        # Ica (11)
        ('1101', 'Ica', '11'),
        ('1102', 'Chincha', '11'),
        ('1103', 'Nasca', '11'),
        ('1104', 'Palpa', '11'),
        ('1105', 'Pisco', '11'),
        
        # Junín (12)
        ('1201', 'Huancayo', '12'),
        ('1202', 'Chanchamayo', '12'),
        ('1203', 'Chupaca', '12'),
        ('1204', 'Jauja', '12'),
        ('1205', 'Junín', '12'),
        ('1206', 'Satipo', '12'),
        ('1207', 'Tarma', '12'),
        ('1208', 'Yauli', '12'),
        
        # La Libertad (13)
        ('1301', 'Trujillo', '13'),
        ('1302', 'Ascope', '13'),
        ('1303', 'Bolívar', '13'),
        ('1304', 'Chepén', '13'),
        ('1305', 'Julcán', '13'),
        ('1306', 'Otuzco', '13'),
        ('1307', 'Pacasmayo', '13'),
        ('1308', 'Pataz', '13'),
        ('1309', 'Sánchez Carrión', '13'),
        ('1310', 'Santiago de Chuco', '13'),
        ('1311', 'Gran Chimú', '13'),
        ('1312', 'Virú', '13'),
        
        # Lambayeque (14)
        ('1401', 'Chiclayo', '14'),
        ('1402', 'Ferreñafe', '14'),
        ('1403', 'Lambayeque', '14'),
        
        # Lima (15)
        ('1501', 'Lima', '15'),
        ('1502', 'Barranca', '15'),
        ('1503', 'Cajatambo', '15'),
        ('1504', 'Canta', '15'),
        ('1505', 'Cañete', '15'),
        ('1506', 'Huaral', '15'),
        ('1507', 'Huarochirí', '15'),
        ('1508', 'Huaura', '15'),
        ('1509', 'Oyón', '15'),
        ('1510', 'Yauyos', '15'),
        
        # Loreto (16)
        ('1601', 'Maynas', '16'),
        ('1602', 'Alto Amazonas', '16'),
        ('1603', 'Datem del Marañón', '16'),
        ('1604', 'Loreto', '16'),
        ('1605', 'Mariscal Ramón Castilla', '16'),
        ('1606', 'Putumayo', '16'),
        ('1607', 'Requena', '16'),
        ('1608', 'Ucayali', '16'),
        
        # Madre de Dios (17)
        ('1701', 'Tambopata', '17'),
        ('1702', 'Manu', '17'),
        ('1703', 'Tahuamanu', '17'),
        
        # Moquegua (18)
        ('1801', 'Mariscal Nieto', '18'),
        ('1802', 'General Sánchez Cerro', '18'),
        ('1803', 'Ilo', '18'),
        
        # Pasco (19)
        ('1901', 'Pasco', '19'),
        ('1902', 'Daniel Alcides Carrión', '19'),
        ('1903', 'Oxapampa', '19'),
        
        # Piura (20)
        ('2001', 'Piura', '20'),
        ('2002', 'Ayabaca', '20'),
        ('2003', 'Huancabamba', '20'),
        ('2004', 'Morropón', '20'),
        ('2005', 'Paita', '20'),
        ('2006', 'Sullana', '20'),
        ('2007', 'Talara', '20'),
        ('2008', 'Sechura', '20'),
        
        # Puno (21)
        ('2101', 'Puno', '21'),
        ('2102', 'Azángaro', '21'),
        ('2103', 'Carabaya', '21'),
        ('2104', 'Chucuito', '21'),
        ('2105', 'El Collao', '21'),
        ('2106', 'Huancané', '21'),
        ('2107', 'Lampa', '21'),
        ('2108', 'Melgar', '21'),
        ('2109', 'Moho', '21'),
        ('2110', 'San Antonio de Putina', '21'),
        ('2111', 'San Román', '21'),
        ('2112', 'Sandia', '21'),
        ('2113', 'Yunguyo', '21'),
        
        # San Martín (22)
        ('2201', 'Moyobamba', '22'),
        ('2202', 'Bellavista', '22'),
        ('2203', 'El Dorado', '22'),
        ('2204', 'Huallaga', '22'),
        ('2205', 'Lamas', '22'),
        ('2206', 'Mariscal Cáceres', '22'),
        ('2207', 'Picota', '22'),
        ('2208', 'Rioja', '22'),
        ('2209', 'San Martín', '22'),
        ('2210', 'Tocache', '22'),
        
        # Tacna (23)
        ('2301', 'Tacna', '23'),
        ('2302', 'Candarave', '23'),
        ('2303', 'Jorge Basadre', '23'),
        ('2304', 'Tarata', '23'),
        
        # Tumbes (24)
        ('2401', 'Tumbes', '24'),
        ('2402', 'Contralmirante Villar', '24'),
        ('2403', 'Zarumilla', '24'),
        
        # Ucayali (25)
        ('2501', 'Coronel Portillo', '25'),
        ('2502', 'Atalaya', '25'),
        ('2503', 'Padre Abad', '25'),
        ('2504', 'Purús', '25'),
    ]
    
    for codigo, nombre, dept_id in provincias:
        try:
            departamento = Departamento.objects.get(id_departamento=dept_id)
            prov, created = Provincia.objects.get_or_create(
                id_provincia=codigo,
                defaults={
                    'nombre': nombre,
                    'id_departamento': departamento
                }
            )
            if created:
                print(f"✓ Provincia creada: {nombre} ({departamento.nombre})")
            else:
                print(f"⚠ Provincia ya existe: {nombre}")
        except Departamento.DoesNotExist:
            print(f"✗ Error: Departamento {dept_id} no encontrado para provincia {nombre}")

def poblar_distritos_principales():
    """Poblar los distritos principales de las capitales de departamento"""
    distritos_principales = [
        # Capitales de departamento (solo algunos ejemplos principales)
        ('010101', 'Chachapoyas', '0101'),
        ('020101', 'Huaraz', '0201'),
        ('030101', 'Abancay', '0301'),
        ('040101', 'Arequipa', '0401'),
        ('050101', 'Ayacucho', '0501'),
        ('060101', 'Cajamarca', '0601'),
        ('070101', 'Callao', '0701'),
        ('080101', 'Cusco', '0801'),
        ('090101', 'Huancavelica', '0901'),
        ('100101', 'Huánuco', '1001'),
        ('110101', 'Ica', '1101'),
        ('120101', 'Huancayo', '1201'),
        ('130101', 'Trujillo', '1301'),
        ('140101', 'Chiclayo', '1401'),
        ('150101', 'Lima', '1501'),
        ('160101', 'Iquitos', '1601'),
        ('170101', 'Tambopata', '1701'),
        ('180101', 'Moquegua', '1801'),
        ('190101', 'Cerro de Pasco', '1901'),
        ('200101', 'Piura', '2001'),
        ('210101', 'Puno', '2101'),
        ('220101', 'Moyobamba', '2201'),
        ('230101', 'Tacna', '2301'),
        ('240101', 'Tumbes', '2401'),
        ('250101', 'Callería', '2501'),
    ]
    
    for codigo, nombre, prov_id in distritos_principales:
        try:
            provincia = Provincia.objects.get(id_provincia=prov_id)
            dist, created = Distrito.objects.get_or_create(
                id_distrito=codigo,
                defaults={
                    'nombre': nombre,
                    'id_provincia': provincia
                }
            )
            if created:
                print(f"✓ Distrito creado: {nombre} ({provincia.nombre})")
            else:
                print(f"⚠ Distrito ya existe: {nombre}")
        except Provincia.DoesNotExist:
            print(f"✗ Error: Provincia {prov_id} no encontrada para distrito {nombre}")

def main():
    """Función principal para poblar toda la información geográfica"""
    print("🌍 Poblando información geográfica del Perú...")
    print("=" * 50)
    
    print("\n📋 1. Poblando departamentos...")
    poblar_departamentos()
    
    print("\n🏛️ 2. Poblando provincias...")
    poblar_provincias()
    
    print("\n🏘️ 3. Poblando distritos principales...")
    poblar_distritos_principales()
    
    print("\n" + "=" * 50)
    print("✅ ¡Poblado completado!")
    
    # Mostrar estadísticas
    total_dept = Departamento.objects.count()
    total_prov = Provincia.objects.count()
    total_dist = Distrito.objects.count()
    
    print(f"\n📊 Estadísticas:")
    print(f"   • Departamentos: {total_dept}")
    print(f"   • Provincias: {total_prov}")
    print(f"   • Distritos: {total_dist}")

if __name__ == '__main__':
    main() 