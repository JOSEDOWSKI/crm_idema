from flask import Flask, render_template, request, send_file, jsonify
import os
import webbrowser
import threading
import time
from datetime import datetime, timedelta
import json
from pdf_generator import generar_pdf_reporte

app = Flask(__name__)

# Crear directorio para reportes si no existe
if not os.path.exists('reportes'):
    os.makedirs('reportes')

@app.route('/')
def index():
    """Página principal con el formulario"""
    return render_template('index.html')

@app.route('/generar_reporte', methods=['POST'])
def generar_reporte():
    """Genera el reporte PDF"""
    try:
        # Obtener datos del formulario
        datos = request.form.to_dict()
        fecha_inicio = datos.get('fecha_inicio')
        fecha_fin = datos.get('fecha_fin')
        tipo_reporte = datos.get('tipo_reporte')
        observaciones = datos.get('observaciones', '')
        
        # Generar nombre de archivo
        if tipo_reporte == 'varios_dias' and fecha_fin and fecha_inicio != fecha_fin:
            filename = f"reporte_{fecha_inicio}_a_{fecha_fin}"
        else:
            filename = f"reporte_{fecha_inicio}"
        
        # Generar PDF directamente usando ReportLab
        pdf_path = generar_pdf_reporte(datos, fecha_inicio, fecha_fin, observaciones, tipo_reporte, filename)
        
        return jsonify({
            'success': True,
            'message': 'Reporte generado exitosamente',
            'filename': f"{filename}.pdf",
            'download_url': f'/descargar/{filename}.pdf'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar el reporte: {str(e)}'
        }), 500

@app.route('/descargar/<filename>')
def descargar_reporte(filename):
    """Descarga el reporte PDF"""
    try:
        file_path = f'reportes/{filename}'
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return "Archivo no encontrado", 404
    except Exception as e:
        return f"Error al descargar: {str(e)}", 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Endpoint para cerrar la aplicación"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Servidor cerrando...'

def abrir_navegador():
    """Abre el navegador después de un pequeño delay"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5002')

if __name__ == '__main__':
    # Abrir navegador en un hilo separado
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    print("=== GENERADOR DE REPORTES ===")
    print("Iniciando aplicación...")
    print("La aplicación se abrirá automáticamente en tu navegador")
    print("Para cerrar la aplicación, cierra esta ventana")
    
    try:
        app.run(debug=False, host='127.0.0.1', port=5002, use_reloader=False)
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")