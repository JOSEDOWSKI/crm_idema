from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import tempfile

def generar_pdf_reporte(datos, fecha_inicio, fecha_fin=None, observaciones="", tipo_reporte="dia_unico", filename="reporte"):
    """
    Genera un reporte PDF usando ReportLab
    """
    # Crear directorio si no existe
    if not os.path.exists('reportes'):
        os.makedirs('reportes')
    
    # Ruta completa del archivo
    pdf_path = f'reportes/{filename}.pdf'
    
    # Crear el documento
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Título principal
    title = Paragraph("Reporte de Métricas Web (idema.edu.pe)", title_style)
    story.append(title)
    
    # Subtítulo con fecha
    if fecha_fin and fecha_inicio != fecha_fin:
        fecha_texto = f"Período del reporte: {fecha_inicio} - {fecha_fin}"
    else:
        fecha_texto = f"Día del reporte: {fecha_inicio}"
    
    subtitle = Paragraph(fecha_texto, subtitle_style)
    story.append(subtitle)
    story.append(Spacer(1, 20))
    
    if tipo_reporte == "varios_dias":
        # Generar reporte de varios días
        generar_contenido_varios_dias(story, datos, styles, section_style)
    else:
        # Generar reporte de un día
        generar_contenido_un_dia(story, datos, styles, section_style)
    
    # Agregar observaciones
    if observaciones.strip():
        story.append(Spacer(1, 30))
        obs_title = Paragraph("Observaciones", section_style)
        story.append(obs_title)
        
        obs_text = Paragraph(observaciones, styles['Normal'])
        story.append(obs_text)
    
    # Construir el PDF
    doc.build(story)
    return pdf_path

def generar_contenido_un_dia(story, datos, styles, section_style):
    """Genera el contenido para reporte de un día"""
    
    # Datos de la tabla
    table_data = [
        ['Métrica', 'Mes Actual', 'Mes Anterior'],
        ['Visitas únicas', datos.get('visitas_unicas_actual', ''), datos.get('visitas_unicas_anterior', '')],
        ['Páginas más vistas', datos.get('paginas_actual', ''), datos.get('paginas_anterior', '')],
        ['Tiempo promedio en el sitio', datos.get('tiempo_actual', ''), datos.get('tiempo_anterior', '')],
        ['Clics al botón de WhatsApp', datos.get('clics_actual', ''), datos.get('clics_anterior', '')],
        ['Dispositivos más usados', datos.get('dispositivos_actual', ''), datos.get('dispositivos_anterior', '')],
        ['Problemas detectados', datos.get('problemas_actual', ''), datos.get('problemas_anterior', '')],
        ['Vendedora más seleccionada', datos.get('vendedora_actual', ''), datos.get('vendedora_anterior', '')],
        ['Test Vocacional', datos.get('test_vocacional', ''), '-'],
        ['Formulario', datos.get('formulario', ''), '-']
    ]
    
    # Crear tabla
    table = Table(table_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    
    # Estilo de la tabla
    table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # Contenido
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Primera columna en negrita
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        
        # Alternar colores de filas
        ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
        ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
        ('BACKGROUND', (0, 6), (-1, 6), colors.lightgrey),
        ('BACKGROUND', (0, 8), (-1, 8), colors.lightgrey),
    ]))
    
    story.append(table)

def generar_contenido_varios_dias(story, datos, styles, section_style):
    """Genera el contenido para reporte de varios días"""
    
    # Extraer datos por día
    dias_datos = extraer_datos_por_dia(datos)
    
    if not dias_datos:
        story.append(Paragraph("No se encontraron datos para el período seleccionado.", styles['Normal']))
        return
    
    # Generar resumen consolidado
    resumen = generar_resumen_consolidado(dias_datos)
    
    # Título del resumen
    resumen_title = Paragraph("Resumen Consolidado", section_style)
    story.append(resumen_title)
    
    # Tabla de resumen
    resumen_data = [
        ['Métrica', 'Promedio/Total del Período'],
        ['Visitas únicas promedio', resumen['visitas_promedio']],
        ['Total de clics WhatsApp', resumen['clics_total']],
        ['Total de formularios', resumen['formularios_total']],
        ['Dispositivo más usado', resumen['dispositivo_mas_usado']],
        ['Vendedora más seleccionada', resumen['vendedora_mas_seleccionada']]
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3*inch, 3*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(resumen_table)
    story.append(Spacer(1, 30))
    
    # Generar gráficos de líneas para estadísticas numéricas
    graficos_title = Paragraph("Tendencias de Estadísticas Numéricas", section_style)
    story.append(graficos_title)
    
    # Generar y agregar gráfico
    grafico_path = generar_grafico_lineas(dias_datos)
    if grafico_path:
        img = Image(grafico_path, width=6*inch, height=4*inch)
        story.append(img)
        story.append(Spacer(1, 20))
        # Limpiar archivo temporal
        try:
            os.remove(grafico_path)
        except:
            pass
    
    # Detalles por día
    detalles_title = Paragraph("Detalles por Día", section_style)
    story.append(detalles_title)
    
    for i, dia_data in enumerate(dias_datos):
        # Título del día
        fecha_formateada = formatear_fecha(dia_data['fecha'])
        dia_title = Paragraph(f"Día {i+1}: {fecha_formateada}", styles['Heading3'])
        story.append(dia_title)
        
        # Tabla del día
        dia_table_data = [
            ['Métrica', 'Valor'],
            ['Visitas únicas', dia_data.get('visitas_unicas', '')],
            ['Páginas más vistas', dia_data.get('paginas_vistas', '')],
            ['Tiempo promedio en el sitio', dia_data.get('tiempo_promedio', '')],
            ['Clics al botón de WhatsApp', dia_data.get('clics_whatsapp', '')],
            ['Dispositivos más usados', dia_data.get('dispositivos', '')],
            ['Problemas detectados', dia_data.get('problemas', '')],
            ['Vendedora más seleccionada', dia_data.get('vendedora', '')],
            ['Test Vocacional', dia_data.get('test_vocacional', '')],
            ['Formularios', dia_data.get('formularios', '')]
        ]
        
        dia_table = Table(dia_table_data, colWidths=[3*inch, 4*inch])
        dia_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(dia_table)
        story.append(Spacer(1, 20))

def extraer_datos_por_dia(datos):
    """Extrae y organiza los datos por día desde el formulario"""
    dias_datos = []
    i = 0
    
    while f'dia_{i}_fecha' in datos:
        dia_data = {
            'fecha': datos.get(f'dia_{i}_fecha', ''),
            'visitas_unicas': datos.get(f'dia_{i}_visitas_unicas', ''),
            'paginas_vistas': datos.get(f'dia_{i}_paginas_vistas', ''),
            'tiempo_promedio': datos.get(f'dia_{i}_tiempo_promedio', ''),
            'clics_whatsapp': datos.get(f'dia_{i}_clics_whatsapp', ''),
            'dispositivos': datos.get(f'dia_{i}_dispositivos', ''),
            'problemas': datos.get(f'dia_{i}_problemas', ''),
            'vendedora': datos.get(f'dia_{i}_vendedora', ''),
            'test_vocacional': datos.get(f'dia_{i}_test_vocacional', ''),
            'formularios': datos.get(f'dia_{i}_formularios', '')
        }
        dias_datos.append(dia_data)
        i += 1
    
    return dias_datos

def generar_resumen_consolidado(dias_datos):
    """Genera un resumen consolidado de todos los días"""
    if not dias_datos:
        return {
            'visitas_promedio': '0',
            'clics_total': '0',
            'formularios_total': '0',
            'dispositivo_mas_usado': 'N/A',
            'vendedora_mas_seleccionada': 'N/A'
        }
    
    # Calcular promedios y totales
    visitas_total = 0
    clics_total = 0
    formularios_total = 0
    dispositivos = {}
    vendedoras = {}
    
    for dia in dias_datos:
        # Visitas únicas
        try:
            visitas = int(dia.get('visitas_unicas', '0'))
            visitas_total += visitas
        except:
            pass
        
        # Clics WhatsApp
        try:
            clics = int(dia.get('clics_whatsapp', '0'))
            clics_total += clics
        except:
            pass
        
        # Formularios
        try:
            forms = int(dia.get('formularios', '0'))
            formularios_total += forms
        except:
            pass
        
        # Dispositivos más usados
        dispositivo = dia.get('dispositivos', '').strip()
        if dispositivo:
            dispositivos[dispositivo] = dispositivos.get(dispositivo, 0) + 1
        
        # Vendedoras
        vendedora = dia.get('vendedora', '').strip()
        if vendedora and vendedora.lower() != 'sin datos':
            vendedoras[vendedora] = vendedoras.get(vendedora, 0) + 1
    
    # Calcular promedios
    num_dias = len(dias_datos)
    visitas_promedio = round(visitas_total / num_dias) if num_dias > 0 else 0
    
    # Encontrar más frecuentes
    dispositivo_mas_usado = max(dispositivos.items(), key=lambda x: x[1])[0] if dispositivos else 'N/A'
    vendedora_mas_seleccionada = max(vendedoras.items(), key=lambda x: x[1])[0] if vendedoras else 'N/A'
    
    return {
        'visitas_promedio': str(visitas_promedio),
        'clics_total': str(clics_total),
        'formularios_total': str(formularios_total),
        'dispositivo_mas_usado': dispositivo_mas_usado,
        'vendedora_mas_seleccionada': vendedora_mas_seleccionada
    }

def formatear_fecha(fecha_str):
    """Formatea una fecha para mostrar"""
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        return f"{fecha.day} de {meses[fecha.month]} de {fecha.year}"
    except:
        return fecha_str

def generar_grafico_lineas(dias_datos):
    """Genera un gráfico de líneas con las estadísticas numéricas"""
    try:
        # Configurar matplotlib para usar un backend sin GUI
        plt.switch_backend('Agg')
        
        # Extraer fechas y datos numéricos
        fechas = []
        visitas = []
        clics = []
        formularios = []
        
        for dia in dias_datos:
            try:
                fecha = datetime.strptime(dia['fecha'], '%Y-%m-%d')
                fechas.append(fecha)
                
                # Visitas únicas
                try:
                    visitas.append(int(dia.get('visitas_unicas', '0')))
                except:
                    visitas.append(0)
                
                # Clics WhatsApp
                try:
                    clics.append(int(dia.get('clics_whatsapp', '0')))
                except:
                    clics.append(0)
                
                # Formularios
                try:
                    formularios.append(int(dia.get('formularios', '0')))
                except:
                    formularios.append(0)
                    
            except:
                continue
        
        if not fechas:
            return None
        
        # Crear el gráfico
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
        fig.suptitle('Tendencias de Estadísticas Numéricas', fontsize=16, fontweight='bold')
        
        # Gráfico de visitas únicas
        ax1.plot(fechas, visitas, marker='o', linewidth=2, markersize=6, color='#1f77b4')
        ax1.set_title('Visitas Únicas por Día', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Visitas')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Gráfico de clics WhatsApp
        ax2.plot(fechas, clics, marker='s', linewidth=2, markersize=6, color='#ff7f0e')
        ax2.set_title('Clics al Botón de WhatsApp por Día', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Clics')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # Gráfico de formularios
        ax3.plot(fechas, formularios, marker='^', linewidth=2, markersize=6, color='#2ca02c')
        ax3.set_title('Formularios Completados por Día', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Formularios')
        ax3.set_xlabel('Fecha')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
        
        # Formatear fechas en el eje x
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar en archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        plt.savefig(temp_file.name, dpi=300, bbox_inches='tight')
        plt.close()
        
        return temp_file.name
        
    except Exception as e:
        print(f"Error generando gráfico: {e}")
        return None