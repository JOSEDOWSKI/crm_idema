import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry, Calendar
import datetime
import os
import subprocess
import json
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MetricaData:
    """Clase para almacenar datos de métricas"""
    visitas_unicas: int
    paginas_mas_vistas: str
    tiempo_promedio: str
    clics_whatsapp: int
    dispositivos_mas_usados: str
    problemas_detectados: str
    vendedora_mas_seleccionada: str
    test_vocacional: str
    formulario: int

class ReporteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Reportes - Análisis de Datos")
        self.root.geometry("800x600")
        
        # Datos de ejemplo (en una aplicación real, estos vendrían de una base de datos)
        self.datos_ejemplo = self.cargar_datos_ejemplo()
        
        self.setup_ui()
    
    def cargar_datos_ejemplo(self) -> Dict[str, MetricaData]:
        """Carga datos de ejemplo para las métricas"""
        return {
            "2024-01-15": MetricaData(
                visitas_unicas=282,
                paginas_mas_vistas="/, idema-educa",
                tiempo_promedio="30seg",
                clics_whatsapp=20,
                dispositivos_mas_usados="Desktop",
                problemas_detectados="301",
                vendedora_mas_seleccionada="Dayana",
                test_vocacional="Vinculado directamente al Form",
                formulario=3
            ),
            "2024-01-14": MetricaData(
                visitas_unicas=234,
                paginas_mas_vistas="/, sobre-nosotros",
                tiempo_promedio="30seg",
                clics_whatsapp=0,
                dispositivos_mas_usados="Desktop",
                problemas_detectados="404",
                vendedora_mas_seleccionada="Sin datos",
                test_vocacional="-",
                formulario=0
            )
        }
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Generador de Reportes de Métricas Web", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sección de selección de fechas
        fecha_frame = ttk.LabelFrame(main_frame, text="Selección de Fechas", padding="10")
        fecha_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Tipo de reporte
        ttk.Label(fecha_frame, text="Tipo de reporte:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.tipo_reporte = tk.StringVar(value="dia_unico")
        ttk.Radiobutton(fecha_frame, text="Reporte de un día", 
                       variable=self.tipo_reporte, value="dia_unico",
                       command=self.cambiar_tipo_reporte).grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(fecha_frame, text="Reporte de varios días", 
                       variable=self.tipo_reporte, value="varios_dias",
                       command=self.cambiar_tipo_reporte).grid(row=1, column=1, sticky=tk.W)
        
        # Fecha única
        self.fecha_unica_frame = ttk.Frame(fecha_frame)
        self.fecha_unica_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(self.fecha_unica_frame, text="Seleccionar fecha:").grid(row=0, column=0, sticky=tk.W)
        self.fecha_unica = DateEntry(self.fecha_unica_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_unica.grid(row=0, column=1, padx=(10, 0))
        
        # Rango de fechas
        self.fecha_rango_frame = ttk.Frame(fecha_frame)
        self.fecha_rango_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(self.fecha_rango_frame, text="Fecha inicio:").grid(row=0, column=0, sticky=tk.W)
        self.fecha_inicio = DateEntry(self.fecha_rango_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_inicio.grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(self.fecha_rango_frame, text="Fecha fin:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.fecha_fin = DateEntry(self.fecha_rango_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_fin.grid(row=0, column=3, padx=(10, 0))
        
        # Inicialmente ocultar el frame de rango
        self.fecha_rango_frame.grid_remove()
        
        # Sección de datos del reporte
        datos_frame = ttk.LabelFrame(main_frame, text="Datos del Reporte", padding="10")
        datos_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Crear campos para editar métricas
        self.crear_campos_metricas(datos_frame)
        
        # Sección de observaciones
        obs_frame = ttk.LabelFrame(main_frame, text="Observaciones", padding="10")
        obs_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.observaciones = tk.Text(obs_frame, height=4, width=70)
        self.observaciones.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.observaciones.insert("1.0", "Disminuyeron las visitas, aun se mantiene por encima del mes anterior pero no sigue la tendencia de subida que tenia, 3 registros del formulario")
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cargar Datos", 
                  command=self.cargar_datos).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Generar Reporte", 
                  command=self.generar_reporte).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Vista Previa", 
                  command=self.vista_previa).grid(row=0, column=2)
    
    def crear_campos_metricas(self, parent):
        """Crea los campos para editar las métricas"""
        self.campos_metricas = {}
        
        metricas = [
            ("Visitas únicas (mes actual)", "visitas_unicas_actual", "282"),
            ("Visitas únicas (mes anterior)", "visitas_unicas_anterior", "234"),
            ("Páginas más vistas (actual)", "paginas_actual", "/, idema-educa"),
            ("Páginas más vistas (anterior)", "paginas_anterior", "/, sobre-nosotros"),
            ("Tiempo promedio (actual)", "tiempo_actual", "30seg"),
            ("Tiempo promedio (anterior)", "tiempo_anterior", "30seg"),
            ("Clics WhatsApp (actual)", "clics_actual", "20"),
            ("Clics WhatsApp (anterior)", "clics_anterior", "Sin datos"),
            ("Dispositivos más usados (actual)", "dispositivos_actual", "Desktop"),
            ("Dispositivos más usados (anterior)", "dispositivos_anterior", "Desktop"),
            ("Problemas detectados (actual)", "problemas_actual", "301"),
            ("Problemas detectados (anterior)", "problemas_anterior", "404"),
            ("Vendedora más seleccionada (actual)", "vendedora_actual", "Dayana"),
            ("Vendedora más seleccionada (anterior)", "vendedora_anterior", "Sin datos"),
            ("Test Vocacional", "test_vocacional", "Vinculado directamente al Form"),
            ("Formulario", "formulario", "3")
        ]
        
        for i, (label, key, default) in enumerate(metricas):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(parent, text=f"{label}:").grid(row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2)
            entry = ttk.Entry(parent, width=20)
            entry.grid(row=row, column=col+1, padx=(0, 20), pady=2)
            entry.insert(0, default)
            self.campos_metricas[key] = entry    

    def cambiar_tipo_reporte(self):
        """Cambia la interfaz según el tipo de reporte seleccionado"""
        if self.tipo_reporte.get() == "dia_unico":
            self.fecha_unica_frame.grid()
            self.fecha_rango_frame.grid_remove()
        else:
            self.fecha_unica_frame.grid_remove()
            self.fecha_rango_frame.grid()
    
    def cargar_datos(self):
        """Carga datos desde archivo o base de datos"""
        # En una implementación real, aquí cargarías datos desde una base de datos
        # Por ahora, solo mostramos un mensaje
        messagebox.showinfo("Cargar Datos", "Funcionalidad para cargar datos desde base de datos")
    
    def obtener_fechas_seleccionadas(self) -> List[datetime.date]:
        """Obtiene las fechas seleccionadas según el tipo de reporte"""
        if self.tipo_reporte.get() == "dia_unico":
            return [self.fecha_unica.get_date()]
        else:
            fechas = []
            fecha_actual = self.fecha_inicio.get_date()
            fecha_fin = self.fecha_fin.get_date()
            
            while fecha_actual <= fecha_fin:
                fechas.append(fecha_actual)
                fecha_actual += datetime.timedelta(days=1)
            
            return fechas
    
    def generar_latex(self, fechas: List[datetime.date]) -> str:
        """Genera el código LaTeX para el reporte"""
        # Obtener datos de los campos
        datos = {}
        for key, entry in self.campos_metricas.items():
            datos[key] = entry.get()
        
        # Determinar el título según el tipo de reporte
        if len(fechas) == 1:
            fecha_str = fechas[0].strftime("%d de %B de %Y")
            titulo_fecha = f"Día del reporte: {fecha_str}"
        else:
            fecha_inicio_str = fechas[0].strftime("%d de %B de %Y")
            fecha_fin_str = fechas[-1].strftime("%d de %B de %Y")
            titulo_fecha = f"Período del reporte: {fecha_inicio_str} - {fecha_fin_str}"
        
        # Obtener observaciones
        observaciones = self.observaciones.get("1.0", tk.END).strip()
        
        latex_content = f"""\\documentclass[12pt]{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{helvet}}
\\renewcommand{{\\familydefault}}{{\\sfdefault}}
\\usepackage{{datetime}}
\\usepackage{{array}}
\\usepackage{{titlesec}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[spanish]{{babel}}

% Date format
\\newdateformat{{customdate}}{{\\THEDAY~de~\\monthname[\\THEMONTH]~de~\\THEYEAR}}

% Title format
\\titleformat{{\\section}}{{\\large\\bfseries}}{{\\thesection}}{{1em}}{{}}

\\begin{{document}}

\\begin{{center}}
\\LARGE \\textbf{{Reporte de Métricas Web (idema.edu.pe)}} \\\\
\\vspace{{0.5em}}
\\large {titulo_fecha}
\\end{{center}}

\\vspace{{1cm}}

\\begin{{tabular}}{{>{{\\bfseries}}p{{5.5cm}} p{{4.5cm}} p{{4.5cm}}}}
\\toprule
\\textbf{{Métrica}} & \\textbf{{Mes Actual}} & \\textbf{{Mes Anterior}} \\\\
\\midrule
Visitas únicas & {datos['visitas_unicas_actual']} & {datos['visitas_unicas_anterior']} \\\\
Páginas más vistas & {datos['paginas_actual']} & {datos['paginas_anterior']} \\\\
Tiempo promedio en el sitio & {datos['tiempo_actual']} & {datos['tiempo_anterior']} \\\\
Clics al botón de WhatsApp & {datos['clics_actual']} & {datos['clics_anterior']} \\\\
Dispositivos más usados & {datos['dispositivos_actual']} & {datos['dispositivos_anterior']} \\\\
Problemas detectados & {datos['problemas_actual']} & {datos['problemas_anterior']} \\\\
Vendedora más seleccionada & {datos['vendedora_actual']} & {datos['vendedora_anterior']} \\\\
Test Vocacional & {datos['test_vocacional']} & - \\\\
Formulario & {datos['formulario']} & - \\\\
\\bottomrule
\\end{{tabular}}

\\vspace{{2cm}}

\\section*{{Observaciones}}

\\vspace{{1em}}

{observaciones}

\\end{{document}}"""
        
        return latex_content
    
    def generar_reporte(self):
        """Genera el reporte en formato LaTeX y PDF"""
        try:
            fechas = self.obtener_fechas_seleccionadas()
            latex_content = self.generar_latex(fechas)
            
            # Crear directorio de reportes si no existe
            if not os.path.exists("reportes"):
                os.makedirs("reportes")
            
            # Generar nombre de archivo
            if len(fechas) == 1:
                filename = f"reporte_{fechas[0].strftime('%Y-%m-%d')}"
            else:
                filename = f"reporte_{fechas[0].strftime('%Y-%m-%d')}_a_{fechas[-1].strftime('%Y-%m-%d')}"
            
            # Guardar archivo LaTeX
            latex_path = f"reportes/{filename}.tex"
            with open(latex_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Intentar compilar a PDF si pdflatex está disponible
            try:
                subprocess.run(['pdflatex', '-output-directory=reportes', latex_path], 
                             check=True, capture_output=True)
                messagebox.showinfo("Éxito", f"Reporte generado exitosamente:\\n{latex_path}\\n{latex_path.replace('.tex', '.pdf')}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                messagebox.showinfo("Reporte Generado", 
                                  f"Archivo LaTeX generado: {latex_path}\\n\\n"
                                  "Para generar el PDF, instala LaTeX y ejecuta:\\n"
                                  f"pdflatex {latex_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el reporte: {str(e)}")
    
    def vista_previa(self):
        """Muestra una vista previa del reporte"""
        try:
            fechas = self.obtener_fechas_seleccionadas()
            latex_content = self.generar_latex(fechas)
            
            # Crear ventana de vista previa
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Vista Previa del Reporte")
            preview_window.geometry("800x600")
            
            # Crear widget de texto con scroll
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insertar contenido
            text_widget.insert("1.0", latex_content)
            text_widget.config(state=tk.DISABLED)
            
            # Botón para guardar
            ttk.Button(preview_window, text="Guardar como...", 
                      command=lambda: self.guardar_como(latex_content)).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar vista previa: {str(e)}")
    
    def guardar_como(self, content):
        """Guarda el reporte con un nombre personalizado"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".tex",
            filetypes=[("LaTeX files", "*.tex"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Éxito", f"Archivo guardado: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

def main():
    root = tk.Tk()
    app = ReporteGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()