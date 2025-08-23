from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, connection, models
from django.contrib import messages
from django.db.models import Count, Sum, Q, F, FloatField, Case, When, Value
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .decorators import rol_requerido, rol_profesor_required, rol_estudiante_required, require_permiso_personalizado
import json
import random
import csv
from datetime import timedelta
from .forms import LeadForm, ConvertirLeadForm, PagoForm, ClienteEditForm, LeadEditForm, InteraccionForm, ObservacionLeadForm, MatriculaEditForm, ObservacionMatriculaForm, NotaForm, AsistenciaForm, EmpleadoForm, EmpleadoConAccesoForm, DocumentoForm
from .models import (
    Lead, LeadInteresPrograma, Cliente, Matricula, Pago, Usuario,
    MedioContacto, Modalidad, MedioPago, ProgramaAcademico,
    Departamento, Provincia, Distrito, ObservacionLead, ObservacionMatricula,
    Nota, Asistencia, Empleado, Documento,
    Curso, PeriodoCurso,
    Ingreso, Gasto, Sede, RolEmpleado, PermisoPersonalizado
)
from django.forms import modelform_factory
from django.urls import reverse
from functools import wraps
from django import forms

def reset_db_connection():
    """Reset database connection to handle cursor errors"""
    try:
        connection.close()
        # Force a new connection
        connection.ensure_connection()
    except Exception:
        pass

def handle_cursor_errors(func):
    """Decorator to handle PostgreSQL cursor errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if 'cursor' in str(e).lower() or 'InvalidCursorName' in str(e):
                reset_db_connection()
                return func(*args, **kwargs)
            raise
    return wrapper

# Create your views here.

@login_required
@require_permiso_personalizado('leads')
def listar_leads(request):
    # Parámetros de búsqueda y filtros
    search_query = request.GET.get('search', '')
    estado_filter = request.GET.get('estado', '')
    medio_filter = request.GET.get('medio', '')
    
    sort_by = request.GET.get('sort', 'fecha_ingreso')
    direction = request.GET.get('direction', 'desc')
    valid_sort_fields = [
        'nombre_completo', 'fecha_ingreso', 'estado_lead', 
        'id_usuario_atencion__nombre_usuario', 'id_medio_contacto__nombre_medio'
    ]
    if sort_by not in valid_sort_fields:
        sort_by = 'fecha_ingreso'
    if direction not in ['asc', 'desc']:
        direction = 'desc'
    sort_map = {
        'nombre_completo': 'l.nombre_completo',
        'fecha_ingreso': 'l.fecha_ingreso',
        'estado_lead': 'l.estado_lead',
        'id_usuario_atencion__nombre_usuario': 'u.nombre_usuario',
        'id_medio_contacto__nombre_medio': 'm.nombre_medio',
    }
    order_by_field = sort_map.get(sort_by, 'l.fecha_ingreso')
    order_by = f"{order_by_field} {'DESC' if direction == 'desc' else 'ASC'}"
    
    # Construir la consulta SQL con filtros
    where_conditions = []
    params = []
    
    if search_query:
        where_conditions.append("(l.nombre_completo ILIKE %s OR l.telefono ILIKE %s)")
        params.extend([f'%{search_query}%', f'%{search_query}%'])
    
    if estado_filter:
        where_conditions.append("l.estado_lead = %s")
        params.append(estado_filter)
    
    if medio_filter:
        where_conditions.append("m.id_medio_contacto = %s")
        params.append(medio_filter)
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    with connection.cursor() as cursor:
        cursor.execute(f'''
            SELECT l.id_lead, l.nombre_completo, l.telefono, l.genero, l.fecha_ingreso, l.estado_lead,
                   u.nombre_usuario, m.nombre_medio
            FROM gestion_lead l
            LEFT JOIN gestion_usuario u ON l.id_usuario_atencion = u.id_usuario
            LEFT JOIN gestion_mediocontacto m ON l.id_medio_contacto = m.id_medio_contacto
            WHERE {where_clause}
            ORDER BY {order_by}
        ''', params)
        rows = cursor.fetchall()
        leads = [
            {
                'id_lead': row[0],
                'nombre_completo': row[1],
                'telefono': row[2],
                'genero': row[3],
                'fecha_ingreso': row[4],
                'estado_lead': row[5],
                'nombre_usuario': row[6],
                'nombre_medio': row[7],
            }
            for row in rows
        ]
    
    # Obtener opciones para filtros
    estados = Lead.ESTADO_LEAD_CHOICES
    medios_contacto = MedioContacto.objects.all()
    
    context = {
        'leads': leads,
        'current_sort': sort_by,
        'current_direction': direction,
        'search_query': search_query,
        'estado_filter': estado_filter,
        'medio_filter': medio_filter,
        'estados': estados,
        'medios_contacto': medios_contacto,
    }
    return render(request, 'gestion/listar_leads.html', context)

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def detalle_lead(request, lead_id):
    lead = get_object_or_404(Lead, id_lead=lead_id)
    
    # Manejar nueva observación
    if request.method == 'POST' and 'agregar_observacion' in request.POST:
        observacion_form = ObservacionLeadForm(request.POST)
        if observacion_form.is_valid():
            observacion = observacion_form.save(commit=False)
            observacion.id_lead = lead
            observacion.id_usuario = request.user.usuario
            observacion.save()
            messages.success(request, f'✅ Observación guardada exitosamente. Ahora tienes {lead.observaciones_lead.count()} observaciones en el historial.')
            return redirect('gestion:detalle_lead', lead_id=lead_id)
        else:
            messages.error(request, '❌ Error al guardar la observación. Por favor, verifica el contenido.')
    else:
        observacion_form = ObservacionLeadForm()
    
    # Obtener observaciones del lead
    observaciones = lead.observaciones_lead.all()
    
    # Estadísticas de observaciones
    total_observaciones = observaciones.count()
    ultima_observacion = observaciones.first()
    observaciones_por_usuario = {}
    
    for obs in observaciones:
        usuario = obs.id_usuario.nombre_usuario
        if usuario in observaciones_por_usuario:
            observaciones_por_usuario[usuario] += 1
        else:
            observaciones_por_usuario[usuario] = 1
    
    context = {
        'lead': lead,
        'observacion_form': observacion_form,
        'observaciones': observaciones,
        'total_observaciones': total_observaciones,
        'ultima_observacion': ultima_observacion,
        'observaciones_por_usuario': observaciones_por_usuario,
    }
    return render(request, 'gestion/detalle_lead.html', context)

@login_required
@require_permiso_personalizado('matriculas')
def listar_matriculas(request):
    # Parámetros de búsqueda y filtros
    search_query = request.GET.get('search', '')
    programa_filter = request.GET.get('programa', '')
    estado_filter = request.GET.get('estado', '')
    
    # Construir la consulta con filtros
    matriculas = Matricula.objects.select_related(
        'id_cliente__id_lead', 
        'id_programa', 
        'id_modalidad'
    )
    
    if search_query:
        matriculas = matriculas.filter(
            Q(id_cliente__id_lead__nombre_completo__icontains=search_query) |
            Q(id_cliente__dni__icontains=search_query)
        )
    
    if programa_filter:
        matriculas = matriculas.filter(id_programa_id=programa_filter)
    
    if estado_filter:
        matriculas = matriculas.filter(estado=estado_filter)
    
    matriculas = matriculas.order_by('-fecha_inscripcion')
    
    # Obtener opciones para filtros
    programas = ProgramaAcademico.objects.all()
    estados = Matricula.EstadoMatricula.choices
    
    context = {
        'matriculas': matriculas,
        'search_query': search_query,
        'programa_filter': programa_filter,
        'estado_filter': estado_filter,
        'programas': programas,
        'estados': estados,
    }
    return render(request, 'gestion/listar_matriculas.html', context)

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def detalle_matricula(request, matricula_id):
    matricula = get_object_or_404(
        Matricula.objects.select_related('id_cliente__id_lead', 'id_programa'),
        id_matricula=matricula_id
    )
    pagos = Pago.objects.filter(id_matricula=matricula_id).order_by('-fecha_pago')

    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.id_matricula = matricula
            pago.save()
            return redirect('gestion:detalle_matricula', matricula_id=matricula_id)
    else:
        form = PagoForm()
    
    context = {
        'matricula': matricula,
        'pagos': pagos,
        'form': form,
    }
    return render(request, 'gestion/detalle_matricula.html', context)

@login_required
@rol_requerido(roles_permitidos=['Admin'])
@transaction.atomic
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id_cliente=cliente_id)
    lead = cliente.id_lead
    
    # Obtener la matrícula del cliente
    try:
        matricula = Matricula.objects.get(id_cliente=cliente)
    except Matricula.DoesNotExist:
        matricula = None

    # Manejar nueva observación de matrícula
    if request.method == 'POST' and 'agregar_observacion_matricula' in request.POST and matricula:
        observacion_form = ObservacionMatriculaForm(request.POST)
        if observacion_form.is_valid():
            observacion = observacion_form.save(commit=False)
            observacion.id_matricula = matricula
            observacion.id_usuario = request.user.usuario
            observacion.save()
            messages.success(request, f'✅ Observación de matrícula guardada exitosamente. Ahora tienes {matricula.observaciones_matricula.count()} observaciones en el historial.')
            return redirect('gestion:editar_cliente', cliente_id=cliente_id)
        else:
            messages.error(request, '❌ Error al guardar la observación. Por favor, verifica el contenido.')
    else:
        observacion_form = ObservacionMatriculaForm()

    # Manejar formularios de edición
    if request.method == 'POST' and 'guardar_cambios' in request.POST:
        cliente_form = ClienteEditForm(request.POST, request.FILES, instance=cliente)
        lead_form = LeadEditForm(request.POST, instance=lead)
        matricula_form = MatriculaEditForm(request.POST, instance=matricula) if matricula else None
        
        forms_valid = cliente_form.is_valid() and lead_form.is_valid()
        if matricula_form:
            forms_valid = forms_valid and matricula_form.is_valid()
        
        if forms_valid:
            cliente_form.save()
            lead_form.save()
            if matricula_form:
                matricula_form.save()
            messages.success(request, f'Se ha actualizado la información de {lead.nombre_completo}.')
            return redirect('gestion:listar_matriculas')
    else:
        cliente_form = ClienteEditForm(instance=cliente)
        lead_form = LeadEditForm(instance=lead)
        matricula_form = MatriculaEditForm(instance=matricula) if matricula else None

    # Obtener observaciones de la matrícula
    observaciones_matricula = []
    if matricula:
        observaciones_matricula = matricula.observaciones_matricula.all()
    
    # Estadísticas de observaciones de matrícula
    total_observaciones_matricula = observaciones_matricula.count()
    ultima_observacion_matricula = observaciones_matricula.first() if observaciones_matricula else None
    observaciones_matricula_por_usuario = {}
    
    for obs in observaciones_matricula:
        usuario = obs.id_usuario.nombre_usuario
        if usuario in observaciones_matricula_por_usuario:
            observaciones_matricula_por_usuario[usuario] += 1
        else:
            observaciones_matricula_por_usuario[usuario] = 1

    context = {
        'cliente_form': cliente_form,
        'lead_form': lead_form,
        'matricula_form': matricula_form,
        'observacion_form': observacion_form,
        'cliente': cliente,
        'matricula': matricula,
        'observaciones_matricula': observaciones_matricula,
        'total_observaciones_matricula': total_observaciones_matricula,
        'ultima_observacion_matricula': ultima_observacion_matricula,
        'observaciones_matricula_por_usuario': observaciones_matricula_por_usuario,
    }
    return render(request, 'gestion/editar_cliente.html', context)

@login_required
@require_permiso_personalizado('poblar_bd')
def poblar_bd_ejemplo(request):
    with connection.cursor() as cursor:
        # Borrar datos
        cursor.execute("DELETE FROM gestion_pago;")
        cursor.execute("DELETE FROM gestion_leadinteresprograma;")
        cursor.execute("DELETE FROM gestion_matricula;")
        cursor.execute("DELETE FROM gestion_cliente;")
        cursor.execute("DELETE FROM gestion_lead;")
        cursor.execute("DELETE FROM gestion_usuario WHERE rol != 'ADMIN';")
        cursor.execute("DELETE FROM gestion_mediocontacto;")
        cursor.execute("DELETE FROM gestion_programaacademico;")
        cursor.execute("DELETE FROM gestion_modalidad;")
        cursor.execute("DELETE FROM gestion_mediopago;")
        cursor.execute("DELETE FROM gestion_distrito;")
        cursor.execute("DELETE FROM gestion_provincia;")
        cursor.execute("DELETE FROM gestion_departamento;")
        # Insertar datos de ejemplo (solo un ejemplo, deberías poblar más según tu lógica)
        cursor.execute("INSERT INTO gestion_departamento (id_departamento, nombre) VALUES ('04', 'AREQUIPA'), ('15', 'LIMA');")
        cursor.execute("INSERT INTO gestion_provincia (id_provincia, nombre, id_departamento) VALUES ('0401', 'AREQUIPA', '04'), ('1501', 'LIMA', '15');")
        cursor.execute("INSERT INTO gestion_distrito (id_distrito, nombre, id_provincia) VALUES ('040101', 'AREQUIPA', '0401'), ('150101', 'LIMA', '1501');")
        cursor.execute("INSERT INTO gestion_mediocontacto (nombre_medio) VALUES ('Facebook'), ('TikTok'), ('Página Web'), ('Familiar'), ('Instagram'), ('Contacto Directo');")
        cursor.execute("INSERT INTO gestion_modalidad (nombre_modalidad) VALUES ('Presencial'), ('Virtual'), ('Semi-presencial');")
        cursor.execute("INSERT INTO gestion_mediopago (nombre_medio) VALUES ('Yape'), ('Tarjeta de Crédito'), ('Transferencia BCP'), ('Efectivo');")
        # ... Agrega más inserts para poblar usuarios, programas, leads, clientes, etc. ...
    messages.success(request, 'La base de datos ha sido reiniciada con datos de ejemplo (SQL puro).')
    return redirect('gestion:dashboard')

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
@transaction.atomic
def convertir_lead_a_cliente(request, lead_id):
    lead = get_object_or_404(Lead, id_lead=lead_id)

    if lead.estado_lead == 'Convertido':
        # Aquí podrías redirigir a una página de error o mostrar un mensaje
        return redirect('gestion:listar_leads')

    if request.method == 'POST':
        form = ConvertirLeadForm(request.POST, request.FILES)
        if form.is_valid():
            sede = form.cleaned_data['sede']
            programa = form.cleaned_data['programa']
            # Validar que el programa pertenezca a la sede seleccionada
            if programa.sede != sede:
                form.add_error('programa', 'El programa seleccionado no pertenece a la sede elegida.')
            else:
                # Crear Cliente
                cliente = Cliente.objects.create(
                    id_lead=lead,
                    dni=form.cleaned_data['dni'],
                    email=form.cleaned_data['email'],
                    archivo_dni=form.cleaned_data.get('archivo_dni'),
                    archivo_partida=form.cleaned_data.get('archivo_partida')
                )

                # Crear usuario Django y Usuario del sistema automáticamente para el alumno
                dni = form.cleaned_data['dni']
                nombres = lead.nombre_completo.split(' ')[0] if lead.nombre_completo else 'Alumno'
                apellidos = ' '.join(lead.nombre_completo.split(' ')[1:]) if lead.nombre_completo and len(lead.nombre_completo.split(' ')) > 1 else 'Sin Apellido'
                email = form.cleaned_data['email']
                
                # Verificar si ya existe un usuario Django con ese username
                user, created = User.objects.get_or_create(
                    username=dni,
                    defaults={'first_name': nombres, 'last_name': apellidos, 'email': email}
                )
                if created:
                    user.set_password(dni)
                    user.save()
                
                # Asignar rol 'Estudiante' o crear uno si no existe
                rol = RolEmpleado.objects.filter(nombre__iexact='Estudiante').first()
                if not rol:
                    rol = RolEmpleado.objects.create(nombre='Estudiante', descripcion='Rol para alumnos matriculados')
                
                # Crear o actualizar el objeto Usuario
                usuario = Usuario.objects.filter(user_django=user).first()
                if not usuario:
                    usuario = Usuario.objects.create(
                        user_django=user,
                        nombre_usuario=f"{nombres} {apellidos}",
                        rol=rol
                    )
                elif not usuario.rol:
                    usuario.rol = rol
                    usuario.save()

                # Crear Matrícula
                matricula = Matricula.objects.create(
                    id_cliente=cliente,
                    id_programa=programa,
                    id_modalidad=form.cleaned_data['modalidad'],
                    observacion=form.cleaned_data['observacion'],
                    id_usuario_inscripcion=lead.id_usuario_atencion
                )

                # --- INICIO DE LA CORRECCIÓN ---
                # Si se incluyó una observación durante la conversión,
                # se crea una entrada en el historial de la matrícula para que no se pierda.
                if matricula.observacion and matricula.observacion.strip():
                    try:
                        # El usuario que registra es el que está logueado
                        usuario_registra = request.user.usuario
                        ObservacionMatricula.objects.create(
                            id_matricula=matricula,
                            id_usuario=usuario_registra,
                            observacion=f"Observación inicial (de la conversión de lead a cliente):\n{matricula.observacion}"
                        )
                    except (AttributeError, Usuario.DoesNotExist):
                        pass
                # --- FIN DE LA CORRECCIÓN ---

                # Actualizar estado del Lead
                lead.estado_lead = 'Convertido'
                lead.save()

                return redirect('gestion:listar_leads')
        # Si hay error, filtrar los programas según la sede seleccionada
        else:
            sede = form.data.get('sede')
            if sede:
                from gestion.models import Sede, ProgramaAcademico
                try:
                    sede_obj = Sede.objects.get(pk=sede)
                    form.fields['programa'].queryset = ProgramaAcademico.objects.filter(sede=sede_obj)
                except Sede.DoesNotExist:
                    form.fields['programa'].queryset = ProgramaAcademico.objects.none()
    else:
        # Pasa los intereses del lead al formulario
        programas_interes = lead.intereses.all()
        form = ConvertirLeadForm(lead_intereses=programas_interes)

    return render(request, 'gestion/convertir_lead.html', {'form': form, 'lead': lead})

@login_required
@require_permiso_personalizado('crear_lead')
def crear_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            # Guardar el lead para obtener un ID
            lead = form.save(commit=False)
            lead.save()

            # Guardar los intereses (relación ManyToMany)
            intereses = form.cleaned_data['intereses']
            for programa in intereses:
                LeadInteresPrograma.objects.create(id_lead=lead, id_programa=programa)

            # --- INICIO DE LA CORRECCIÓN ---
            # Si se incluyó una observación general en el formulario de creación,
            # se crea una entrada en el historial de observaciones para que no se pierda.
            if lead.observaciones and lead.observaciones.strip():
                try:
                    # El usuario que registra la observación es el que está logueado.
                    usuario_registra = request.user.usuario
                    ObservacionLead.objects.create(
                        id_lead=lead,
                        id_usuario=usuario_registra,
                        observacion=f"Observación inicial (del formulario de creación):\n{lead.observaciones}"
                    )
                except (AttributeError, Usuario.DoesNotExist):
                    # Fallback por si request.user.usuario no existe o no está bien configurado.
                    # En una aplicación real, se podría registrar este evento.
                    pass
            # --- FIN DE LA CORRECCIÓN ---

            # Redirigir a una página de éxito o a la lista de leads
            return redirect('gestion:listar_leads')
    else:
        form = LeadForm()

    return render(request, 'gestion/crear_lead.html', {'form': form})

@login_required
@require_permiso_personalizado('dashboard')
def superadmin_dashboard(request):
    """Dashboard especial para superusuarios con información detallada del sistema"""
    context = {}
    
    try:
        with connection.cursor() as cursor:
            # === ESTADÍSTICAS GENERALES ===
            cursor.execute("SELECT COUNT(*) FROM gestion_lead;")
            total_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM gestion_cliente;")
            total_clientes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM gestion_matricula;")
            total_matriculas = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM gestion_pago;")
            total_pagos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM gestion_usuario WHERE activo = true;")
            usuarios_activos = cursor.fetchone()[0]
            
            # === ESTADÍSTICAS FINANCIERAS ===
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM gestion_pago;")
            total_recaudado = cursor.fetchone()[0]
            
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM gestion_pago WHERE EXTRACT(YEAR FROM fecha_pago) = EXTRACT(YEAR FROM NOW()) AND EXTRACT(MONTH FROM fecha_pago) = EXTRACT(MONTH FROM NOW());")
            recaudado_este_mes = cursor.fetchone()[0]
            
            # === ESTADÍSTICAS DE CONVERSIÓN ===
            tasa_conversion = (total_clientes / total_leads * 100) if total_leads > 0 else 0
            
            cursor.execute("SELECT COUNT(*) FROM gestion_matricula WHERE estado = 'Activo';")
            matriculas_activas = cursor.fetchone()[0]
            
            tasa_retencion = (matriculas_activas / total_matriculas * 100) if total_matriculas > 0 else 0
            
            # === ESTADÍSTICAS POR MES ===
            now = timezone.now()
            cursor.execute("""
                SELECT EXTRACT(MONTH FROM fecha_ingreso) as mes, COUNT(*) as cantidad
                FROM gestion_lead 
                WHERE EXTRACT(YEAR FROM fecha_ingreso) = %s
                GROUP BY EXTRACT(MONTH FROM fecha_ingreso)
                ORDER BY mes
            """, [now.year])
            leads_por_mes = cursor.fetchall()
            
            # === TOP PROGRAMAS ===
            cursor.execute("""
                SELECT p.nombre_programa, COUNT(m.id_matricula) as matriculas
                FROM gestion_programaacademico p
                LEFT JOIN gestion_matricula m ON p.id_programa = m.id_programa
                GROUP BY p.id_programa, p.nombre_programa
                ORDER BY matriculas DESC
                LIMIT 5
            """)
            top_programas = cursor.fetchall()
            
            # === TOP ASESORES ===
            cursor.execute("""
                SELECT u.nombre_usuario, COUNT(l.id_lead) as leads, COUNT(c.id_cliente) as conversiones
                FROM gestion_usuario u
                LEFT JOIN gestion_lead l ON u.id_usuario = l.id_usuario_atencion
                LEFT JOIN gestion_cliente c ON l.id_lead = c.id_lead_id
                WHERE u.rol = 'VENTAS'
                GROUP BY u.id_usuario, u.nombre_usuario
                ORDER BY leads DESC
                LIMIT 5
            """)
            top_asesores = cursor.fetchall()
            
            # === ESTADÍSTICAS DE LA BASE DE DATOS ===
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            total_tablas = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            tamano_bd = cursor.fetchone()[0]
            
            # === ÚLTIMAS ACTIVIDADES ===
            cursor.execute("""
                SELECT 'Lead' as tipo, l.nombre_completo, l.fecha_ingreso, u.nombre_usuario
                FROM gestion_lead l
                LEFT JOIN gestion_usuario u ON l.id_usuario_atencion = u.id_usuario
                ORDER BY l.fecha_ingreso DESC
                LIMIT 5
            """)
            ultimas_actividades = cursor.fetchall()
            
            # === ESTADÍSTICAS DE PAGOS ===
            cursor.execute("""
                SELECT concepto, COUNT(*) as cantidad, SUM(monto) as total
                FROM gestion_pago
                GROUP BY concepto
                ORDER BY total DESC
            """)
            estadisticas_pagos = cursor.fetchall()
            
            context.update({
                # Estadísticas generales
                'total_leads': total_leads,
                'total_clientes': total_clientes,
                'total_matriculas': total_matriculas,
                'total_pagos': total_pagos,
                'usuarios_activos': usuarios_activos,
                
                # Estadísticas financieras
                'total_recaudado': total_recaudado,
                'recaudado_este_mes': recaudado_este_mes,
                
                # Tasas de conversión
                'tasa_conversion': round(tasa_conversion, 2),
                'tasa_retencion': round(tasa_retencion, 2),
                'matriculas_activas': matriculas_activas,
                
                # Datos para gráficos
                'leads_por_mes': leads_por_mes,
                'top_programas': top_programas,
                'top_asesores': top_asesores,
                
                # Información del sistema
                'total_tablas': total_tablas,
                'tamano_bd': tamano_bd,
                
                # Actividades recientes
                'ultimas_actividades': ultimas_actividades,
                'estadisticas_pagos': estadisticas_pagos,
                
                # Año actual
                'ano_actual': now.year,
            })
            
    except Exception as e:
        context['error'] = f"Error al cargar estadísticas: {e}"
    
    return render(request, 'gestion/superadmin_dashboard.html', context)

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def exportar_leads_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="listado_leads.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow([
        'Nombre Completo', 'Telefono', 'Email', 'Genero', 'Estado', 
        'Asesor Asignado', 'Medio de Contacto', 'Distrito', 'Fecha de Ingreso', 'Observaciones Generales'
    ])
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT l.nombre_completo, l.telefono, c.email, l.genero, l.estado_lead, 
                   u.nombre_usuario, m.nombre_medio, d.nombre, l.fecha_ingreso, l.observaciones
            FROM gestion_lead l
            LEFT JOIN gestion_cliente c ON l.id_lead = c.id_lead_id
            LEFT JOIN gestion_usuario u ON l.id_usuario_atencion = u.id_usuario
            LEFT JOIN gestion_mediocontacto m ON l.id_medio_contacto = m.id_medio_contacto
            LEFT JOIN gestion_distrito d ON l.id_distrito = d.id_distrito
        ''')
        for row in cursor.fetchall():
            writer.writerow([
                row[0], row[1], row[2], row[3], row[4],
                row[5] if row[5] else 'N/A',
                row[6] if row[6] else 'N/A',
                row[7] if row[7] else 'N/A',
                row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else '',
                row[9] if row[9] else ''
            ])
    return response

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def exportar_matriculas_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="listado_matriculas.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow([
        'Nombre Completo', 'DNI', 'Email', 'Programa', 'Modalidad', 'Estado', 
        'Fecha Inscripción', 'Usuario Inscripción', 'Observación'
    ])
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT l.nombre_completo, c.dni, c.email, p.nombre_programa, 
                   m.nombre_modalidad, mat.estado, mat.fecha_inscripcion, 
                   u.nombre_usuario, mat.observacion
            FROM gestion_matricula mat
            JOIN gestion_cliente c ON mat.id_cliente = c.id_cliente
            JOIN gestion_lead l ON c.id_lead_id = l.id_lead
            JOIN gestion_programaacademico p ON mat.id_programa = p.id_programa
            JOIN gestion_modalidad m ON mat.id_modalidad = m.id_modalidad
            JOIN gestion_usuario u ON mat.id_usuario_inscripcion = u.id_usuario
            ORDER BY mat.fecha_inscripcion DESC
        ''')
        for row in cursor.fetchall():
            writer.writerow([
                row[0], row[1], row[2], row[3], row[4], row[5],
                row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else '',
                row[7] if row[7] else 'N/A',
                row[8] if row[8] else ''
            ])
    return response

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def exportar_observaciones_csv(request, lead_id):
    lead = get_object_or_404(Lead, id_lead=lead_id)
    observaciones = lead.observaciones_lead.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="observaciones_{lead.nombre_completo.replace(" ", "_")}.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    
    writer.writerow([
        'Fecha y Hora', 'Usuario', 'Observación'
    ])
    
    for obs in observaciones:
        writer.writerow([
            obs.fecha_observacion.strftime('%Y-%m-%d %H:%M:%S'),
            obs.id_usuario.nombre_usuario,
            obs.observacion
        ])
    
    return response

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def exportar_observaciones_matricula_csv(request, matricula_id):
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    observaciones = matricula.observaciones_matricula.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="observaciones_matricula_{matricula.id_cliente.id_lead.nombre_completo.replace(" ", "_")}.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    
    writer.writerow([
        'Fecha y Hora', 'Usuario', 'Observación'
    ])
    
    for obs in observaciones:
        writer.writerow([
            obs.fecha_observacion.strftime('%Y-%m-%d %H:%M:%S'),
            obs.id_usuario.nombre_usuario,
            obs.observacion
        ])
    
    return response

# ==============================================================
# VISTAS ACADÉMICAS (PERÍODOS, NOTAS Y ASISTENCIAS)
# ==============================================================

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
@handle_cursor_errors
def gestionar_notas_matricula(request, matricula_id):
    """Vista para gestionar notas de una matrícula específica"""
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    try:
        pagos_pension = list(Pago.objects.filter(
            id_matricula=matricula,
            concepto='Pensión'
        ).values_list('numero_cuota', flat=True).distinct())
        max_cuota_pagada = max(pagos_pension) if pagos_pension else 0
        periodo_actual = max_cuota_pagada + 1
        max_periodos_programa = matricula.id_programa.numero_pensiones
        periodo_actual = min(periodo_actual, max_periodos_programa)
        periodos = list(PeriodoCurso.objects.filter(
            programa=matricula.id_programa,
            numero_mes__lte=periodo_actual,
            activo=True
        ).order_by('numero_mes'))
        notas = list(Nota.objects.filter(id_matricula=matricula).order_by('-fecha_registro'))
    except Exception as e:
        reset_db_connection()
        pagos_pension = list(Pago.objects.filter(
            id_matricula=matricula,
            concepto='Pensión'
        ).values_list('numero_cuota', flat=True).distinct())
        max_cuota_pagada = max(pagos_pension) if pagos_pension else 0
        periodo_actual = max_cuota_pagada + 1
        max_periodos_programa = matricula.id_programa.numero_pensiones
        periodo_actual = min(periodo_actual, max_periodos_programa)
        periodos = list(PeriodoCurso.objects.filter(
            programa=matricula.id_programa,
            numero_mes__lte=periodo_actual,
            activo=True
        ).order_by('numero_mes'))
        notas = list(Nota.objects.filter(id_matricula=matricula).order_by('-fecha_registro'))
    if request.method == 'POST' and 'agregar_nota' in request.POST:
        nota_form = NotaForm(request.POST)
        if nota_form.is_valid():
            nota = nota_form.save(commit=False)
            nota.id_matricula = matricula
            nota.id_usuario_registro = request.user.usuario
            if nota.puede_recibir_nota:
                nota.save()
                messages.success(request, f'✅ Nota {nota.nota} registrada exitosamente para {nota.tipo_nota}.')
            else:
                messages.warning(request, '⚠️ El alumno debe estar al día con los pagos para recibir notas.')
            return redirect('gestion:gestionar_notas_matricula', matricula_id=matricula_id)
        else:
            messages.error(request, '❌ Error al registrar la nota. Por favor, verifica los datos.')
    else:
        nota_form = NotaForm()
        nota_form.fields['periodo_curso'].queryset = PeriodoCurso.objects.filter(
            programa=matricula.id_programa,
            numero_mes__lte=periodo_actual,
            activo=True
        ).order_by('numero_mes')
    total_notas = len(notas)
    if notas:
        promedio_notas = sum(nota.nota for nota in notas) / total_notas
        notas_aprobadas = sum(1 for nota in notas if nota.nota >= 14)
        notas_desaprobadas = sum(1 for nota in notas if nota.nota < 14)
    else:
        promedio_notas = 0
        notas_aprobadas = 0
        notas_desaprobadas = 0
    context = {
        'matricula': matricula,
        'nota_form': nota_form,
        'notas': notas,
        'periodos': periodos,
        'total_notas': total_notas,
        'promedio_notas': round(promedio_notas, 2),
        'notas_aprobadas': notas_aprobadas,
        'notas_desaprobadas': notas_desaprobadas,
    }
    return render(request, 'gestion/gestionar_notas.html', context)

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
@handle_cursor_errors
def gestionar_asistencias_matricula(request, matricula_id):
    """Vista para gestionar asistencias de una matrícula específica"""
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    try:
        pagos_pension = list(Pago.objects.filter(
            id_matricula=matricula,
            concepto='Pensión'
        ).values_list('numero_cuota', flat=True).distinct())
        max_cuota_pagada = max(pagos_pension) if pagos_pension else 0
        periodo_actual = max_cuota_pagada + 1
        max_periodos_programa = matricula.id_programa.numero_pensiones
        periodo_actual = min(periodo_actual, max_periodos_programa)
        periodos = list(PeriodoCurso.objects.filter(
            programa=matricula.id_programa,
            numero_mes__lte=periodo_actual,
            activo=True
        ).order_by('numero_mes'))
        asistencias = list(Asistencia.objects.filter(id_matricula=matricula).order_by('-fecha_clase'))
    except Exception as e:
        reset_db_connection()
        pagos_pension = list(Pago.objects.filter(
            id_matricula=matricula,
            concepto='Pensión'
        ).values_list('numero_cuota', flat=True).distinct())
        max_cuota_pagada = max(pagos_pension) if pagos_pension else 0
        periodo_actual = max_cuota_pagada + 1
        max_periodos_programa = matricula.id_programa.numero_pensiones
        periodo_actual = min(periodo_actual, max_periodos_programa)
        periodos = list(PeriodoCurso.objects.filter(
            programa=matricula.id_programa,
            numero_mes__lte=periodo_actual,
            activo=True
        ).order_by('numero_mes'))
        asistencias = list(Asistencia.objects.filter(id_matricula=matricula).order_by('-fecha_clase'))
    if request.method == 'POST' and 'agregar_asistencia' in request.POST:
        asistencia_form = AsistenciaForm(request.POST)
        if asistencia_form.is_valid():
            asistencia = asistencia_form.save(commit=False)
            asistencia.id_matricula = matricula
            asistencia.id_usuario_registro = request.user.usuario
            asistencia.save()
            messages.success(request, f'✅ Asistencia registrada exitosamente para {asistencia.fecha_clase}.')
            return redirect('gestion:gestionar_asistencias_matricula', matricula_id=matricula_id)
        else:
            messages.error(request, '❌ Error al registrar la asistencia. Por favor, verifica los datos.')
    else:
        asistencia_form = AsistenciaForm()
        asistencia_form.fields['periodo_curso'].queryset = PeriodoCurso.objects.filter(
            programa=matricula.id_programa,
            numero_mes__lte=periodo_actual,
            activo=True
        ).order_by('numero_mes')
    total_clases = len(asistencias)
    if asistencias:
        clases_asistidas = sum(1 for asistencia in asistencias if asistencia.asistio)
        clases_faltadas = sum(1 for asistencia in asistencias if not asistencia.asistio)
        porcentaje_asistencia = (clases_asistidas / total_clases * 100) if total_clases > 0 else 0
    else:
        clases_asistidas = 0
        clases_faltadas = 0
        porcentaje_asistencia = 0
    context = {
        'matricula': matricula,
        'asistencia_form': asistencia_form,
        'asistencias': asistencias,
        'periodos': periodos,
        'total_clases': total_clases,
        'clases_asistidas': clases_asistidas,
        'clases_faltadas': clases_faltadas,
        'porcentaje_asistencia': round(porcentaje_asistencia, 1),
    }
    return render(request, 'gestion/gestionar_asistencias.html', context)

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def exportar_notas_csv(request, matricula_id):
    """Exportar notas de una matrícula a CSV"""
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    notas = matricula.notas.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="notas_{matricula.id_cliente.id_lead.nombre_completo.replace(" ", "_")}.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow([
        'Programa Académico', 'Nombre del Alumno', 'DNI', 'Mes', 'Curso', 'Tipo de Nota', 'Nota', 'Estado', 'Observaciones', 'Fecha de Registro', 'Usuario'
    ])
    for nota in notas:
        if nota.periodo_curso:
            mes = nota.periodo_curso.numero_mes
            curso_nombre = nota.periodo_curso.curso.nombre
        else:
            mes = '-'
            curso_nombre = '-'
        writer.writerow([
            matricula.id_programa.nombre_programa,
            matricula.id_cliente.id_lead.nombre_completo,
            matricula.id_cliente.dni,
            mes,
            curso_nombre,
            nota.tipo_nota,
            nota.nota,
            nota.estado_nota,
            nota.observaciones or '',
            nota.fecha_registro.strftime('%Y-%m-%d %H:%M:%S'),
            nota.id_usuario_registro.nombre_usuario,
        ])
    return response

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def exportar_asistencias_csv(request, matricula_id):
    """Exportar asistencias de una matrícula a CSV"""
    matricula = get_object_or_404(Matricula, id_matricula=matricula_id)
    asistencias = matricula.asistencias.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="asistencias_{matricula.id_cliente.id_lead.nombre_completo.replace(" ", "_")}.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow([
        'Mes', 'Curso', 'Fecha de Clase', 'Asistió', 'Justificación', 'Fecha de Registro', 'Usuario'
    ])
    for asistencia in asistencias:
        if asistencia.periodo_curso:
            mes = asistencia.periodo_curso.numero_mes
            curso_nombre = asistencia.periodo_curso.curso.nombre
        else:
            mes = '-'
            curso_nombre = '-'
        writer.writerow([
            mes,
            curso_nombre,
            asistencia.fecha_clase.strftime('%Y-%m-%d'),
            'Sí' if asistencia.asistio else 'No',
            asistencia.justificacion or '',
            asistencia.fecha_registro.strftime('%Y-%m-%d %H:%M:%S'),
            asistencia.id_usuario_registro.nombre_usuario,
        ])
    return response

def login_view(request):
    if request.user.is_authenticated:
        return redirect('gestion:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('gestion:dashboard')
            else:
                messages.error(request,"Usuario o contraseña inválidos.")
        else:
            messages.error(request,"Usuario o contraseña inválidos.")
    form = AuthenticationForm()
    return render(request, 'gestion/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect('gestion:login')

@login_required
def no_access_view(request):
    return render(request, 'gestion/no_access.html')

# Helper decorator para superuser
def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func

@superuser_required
def gestionar_roles(request):
    roles = RolEmpleado.objects.all()
    return render(request, 'gestion/rrhh/gestionar_roles.html', {'roles': roles})

@superuser_required
def crear_rol(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        permisos = request.POST.getlist('permisos')
        rol = RolEmpleado.objects.create(nombre=nombre, descripcion=descripcion)
        if permisos:
            rol.permisos.set(permisos)
        return redirect('gestion:gestionar_roles')
    permisos = PermisoPersonalizado.objects.all()
    return render(request, 'gestion/rrhh/form_rol.html', {'permisos': permisos, 'accion': 'Crear'})

@superuser_required
def editar_rol(request, rol_id):
    rol = RolEmpleado.objects.get(id=rol_id)
    if request.method == 'POST':
        rol.nombre = request.POST.get('nombre')
        rol.descripcion = request.POST.get('descripcion')
        permisos = request.POST.getlist('permisos')
        rol.save()
        rol.permisos.set(permisos)
        return redirect('gestion:gestionar_roles')
    permisos = PermisoPersonalizado.objects.all()
    return render(request, 'gestion/rrhh/form_rol.html', {'rol': rol, 'permisos': permisos, 'accion': 'Editar'})

@superuser_required
def eliminar_rol(request, rol_id):
    rol = RolEmpleado.objects.get(id=rol_id)
    if request.method == 'POST':
        rol.delete()
        return redirect('gestion:gestionar_roles')
    return render(request, 'gestion/rrhh/delete_rol.html', {'rol': rol})

# Modelos de catálogo
CATALOG_MODELS = [
    ('departamento', Departamento),
    ('provincia', Provincia),
    ('distrito', Distrito),
    ('programa', ProgramaAcademico),
    ('modalidad', Modalidad),
    ('mediocontacto', MedioContacto),
    ('mediopago', MedioPago),
]

# Listar
@superuser_required
def catalogo_list(request, modelo):
    model = dict(CATALOG_MODELS).get(modelo)
    if not model:
        return HttpResponseForbidden('Catálogo no válido.')
    objetos = model.objects.all()
    return render(request, f'gestion/catalogos/list_{modelo}.html', {'objetos': objetos, 'modelo': modelo})

# Crear
@superuser_required
def catalogo_create(request, modelo):
    model = dict(CATALOG_MODELS).get(modelo)
    if not model:
        return HttpResponseForbidden('Catálogo no válido.')
    Form = modelform_factory(model, exclude=())
    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('gestion:catalogo_list', args=[modelo]))
    else:
        form = Form()
    return render(request, f'gestion/catalogos/form_{modelo}.html', {'form': form, 'modelo': modelo, 'accion': 'Crear'})

# Editar
@superuser_required
def catalogo_edit(request, modelo, pk):
    model = dict(CATALOG_MODELS).get(modelo)
    if not model:
        return HttpResponseForbidden('Catálogo no válido.')
    obj = get_object_or_404(model, pk=pk)
    Form = modelform_factory(model, exclude=())
    if request.method == 'POST':
        form = Form(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('gestion:catalogo_list', args=[modelo]))
    else:
        form = Form(instance=obj)
    return render(request, f'gestion/catalogos/form_{modelo}.html', {'form': form, 'modelo': modelo, 'accion': 'Editar'})

# Eliminar
@superuser_required
def catalogo_delete(request, modelo, pk):
    model = dict(CATALOG_MODELS).get(modelo)
    if not model:
        return HttpResponseForbidden('Catálogo no válido.')
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(reverse('gestion:catalogo_list', args=[modelo]))
    return render(request, f'gestion/catalogos/delete_{modelo}.html', {'obj': obj, 'modelo': modelo})

@login_required
@require_permiso_personalizado('empleados')
def listar_empleados(request):
    empleados = Empleado.objects.all().order_by('apellidos', 'nombres')
    return render(request, 'gestion/rrhh/listar_empleados.html', {'empleados': empleados})

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            empleado = form.save(commit=False)
            from django.contrib.auth.models import User
            from gestion.models import Usuario, RolEmpleado
            # Crear usuario Django y Usuario del sistema automáticamente
            dni = form.cleaned_data['dni']
            nombres = form.cleaned_data['nombres']
            apellidos = form.cleaned_data['apellidos']
            email = form.cleaned_data.get('email') or ''
            # Verificar si ya existe un usuario Django con ese username
            user, created = User.objects.get_or_create(
                username=dni,
                defaults={'first_name': nombres, 'last_name': apellidos, 'email': email}
            )
            if created:
                user.set_password(dni)
                user.save()
            # Asignar rol por defecto (por ejemplo, el primero que no sea Admin)
            rol = RolEmpleado.objects.exclude(nombre__iexact='Admin').first()
            if not rol:
                rol = RolEmpleado.objects.create(nombre='Empleado', descripcion='Rol por defecto para empleados')
            usuario = Usuario.objects.filter(user_django=user).first()
            if not usuario:
                usuario = Usuario.objects.create(
                    user_django=user,
                    nombre_usuario=f"{nombres} {apellidos}",
                    rol=rol
                )
            elif not usuario.rol:
                usuario.rol = rol
                usuario.save()
            empleado.usuario = usuario
            empleado.save()
            return redirect('gestion:listar_empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'gestion/form_empleado.html', {'form': form})

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def editar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('gestion:listar_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'gestion/form_empleado.html', {'form': form, 'empleado': empleado})

@login_required
@rol_requerido(roles_permitidos=['Admin'])
def eliminar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    if request.method == 'POST':
        empleado.delete()
        return redirect('gestion:listar_empleados')
    return render(request, 'gestion/rrhh/delete_empleado.html', {'empleado': empleado})

@login_required
def detalle_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    return render(request, 'gestion/rrhh/detalle_empleado.html', {'empleado': empleado})

@login_required
@require_permiso_personalizado('nuevo_empleado')
def crear_empleado_con_acceso(request):
    if request.method == 'POST':
        form = EmpleadoConAccesoForm(request.POST)
        if form.is_valid():
            # Crear User de Django
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['dni']
            )
            # Crear Usuario del sistema
            rol = form.cleaned_data['rol']
            usuario = Usuario.objects.create(
                user_django=user,
                nombre_usuario=f"{form.cleaned_data['nombres']} {form.cleaned_data['apellidos']}",
                rol=rol,
                activo=True
            )
            # Asignar permisos personalizados: los del rol + los seleccionados manualmente (sin duplicados)
            permisos_rol = list(rol.permisos.all())
            permisos_form = list(form.cleaned_data.get('permisos')) if form.cleaned_data.get('permisos') else []
            permisos_finales = set(permisos_rol + permisos_form)
            usuario.permisos_personalizados.set(permisos_finales)
            # Crear ficha de empleado
            Empleado.objects.create(
                usuario=usuario,
                nombres=form.cleaned_data['nombres'],
                apellidos=form.cleaned_data['apellidos'],
                dni=form.cleaned_data['dni'],
                cargo=form.cleaned_data['cargo'],
                fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
                direccion=form.cleaned_data.get('direccion'),
                telefono=form.cleaned_data.get('telefono'),
                banco=form.cleaned_data.get('banco'),
                cuenta_bancaria=form.cleaned_data.get('cuenta_bancaria'),
                cci=form.cleaned_data.get('cci'),
                fecha_ingreso=form.cleaned_data.get('fecha_ingreso'),
                tipo_contrato=form.cleaned_data.get('tipo_contrato'),
                horas_contrato=form.cleaned_data.get('horas_contrato') or 0,
                sueldo_basico=form.cleaned_data.get('sueldo_basico') or 0,
                sueldo_por_hora=form.cleaned_data.get('sueldo_por_hora') or 0,
                horas_extras=form.cleaned_data.get('horas_extras') or 0,
                inasistencias=form.cleaned_data.get('inasistencias') or 0,
                comisiones=form.cleaned_data.get('comisiones') or 0,
                bonos=form.cleaned_data.get('bonos') or 0,
                descuentos=form.cleaned_data.get('descuentos') or 0,
                remuneracion_bruta=form.cleaned_data.get('remuneracion_bruta') or 0,
                neto_mensual=form.cleaned_data.get('neto_mensual') or 0,
                neto_quincenal=form.cleaned_data.get('neto_quincenal') or 0,
                aporte_empleador=form.cleaned_data.get('aporte_empleador') or 0,
            )
            return render(request, 'gestion/rrhh/empleado_creado.html', {'username': user.username, 'password': form.cleaned_data['dni']})
    else:
        form = EmpleadoConAccesoForm()
    return render(request, 'gestion/rrhh/form_empleado_con_acceso.html', {'form': form})

@login_required
@require_permiso_personalizado('documentacion')
def listar_documentos(request):
    empleado_id = request.GET.get('empleado_id', '')
    mes = request.GET.get('mes', '')  # Formato esperado: 'YYYY-MM'

    documentos = Documento.objects.select_related('empleado').order_by('-fecha_subida')

    if empleado_id:
        documentos = documentos.filter(empleado_id=empleado_id)
    if mes:
        try:
            year, month = map(int, mes.split('-'))
            documentos = documentos.filter(fecha_subida__year=year, fecha_subida__month=month)
        except ValueError:
            pass  # Si el formato es incorrecto, ignora el filtro

    # Lista de empleados únicos con documentos
    empleados = Empleado.objects.filter(documentos__isnull=False).distinct().order_by('apellidos', 'nombres')

    # Lista de meses únicos con documentos (YYYY-MM)
    from django.db.models.functions import TruncMonth
    from django.db.models import DateTimeField
    meses = (
        Documento.objects.annotate(mes=TruncMonth('fecha_subida', output_field=DateTimeField()))
        .values_list('mes', flat=True).distinct().order_by('-mes')
    )

    return render(request, 'gestion/documentos/listar_documentos.html', {
        'documentos': documentos,
        'empleados': empleados,
        'meses': meses,
        'empleado_id': empleado_id,
        'mes': mes,
    })

@login_required
def subir_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            empleado = Empleado.objects.get(usuario__user_django=request.user)
            doc = form.save(commit=False)
            doc.empleado = empleado
            doc.save()
            return redirect('gestion:listar_documentos')
    else:
        form = DocumentoForm()
    return render(request, 'gestion/documentos/subir_documento.html', {'form': form})

@login_required
def detalle_documento(request, documento_id):
    doc = Documento.objects.select_related('empleado').get(id=documento_id)
    return render(request, 'gestion/documentos/detalle_documento.html', {'doc': doc})

@superuser_required
def resenar_documento(request, documento_id):
    doc = Documento.objects.get(id=documento_id)
    if request.method == 'POST':
        resena = request.POST.get('resena_admin', '').strip()
        if resena:
            doc.resena_admin = resena
            doc.fecha_resena = timezone.now()
            doc.usuario_admin_resena = request.user.usuario
            doc.save()
            return redirect('gestion:detalle_documento', documento_id=doc.id)
    return render(request, 'gestion/documentos/resenar_documento.html', {'doc': doc})

@login_required
@require_permiso_personalizado('malla_curricular')
def listar_programas_malla(request):
    programas = ProgramaAcademico.objects.all().order_by('nombre_programa')
    return render(request, 'gestion/listar_programas_malla.html', {'programas': programas})

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def editar_malla_curricular(request, programa_id):
    programa = get_object_or_404(ProgramaAcademico, pk=programa_id)
    duracion = programa.duracion_meses
    # Crear PeriodoCurso vacíos si faltan
    existentes = PeriodoCurso.objects.filter(programa=programa).count()
    if existentes < duracion:
        for mes in range(existentes + 1, duracion + 1):
            PeriodoCurso.objects.get_or_create(programa=programa, numero_mes=mes, defaults={
                'curso': Curso.objects.first() if Curso.objects.exists() else Curso.objects.create(nombre=f'Curso {mes}')
            })
    malla = PeriodoCurso.objects.filter(programa=programa).order_by('numero_mes')
    if request.method == 'POST':
        for pc in malla:
            nombre_curso = request.POST.get(f'nombre_curso_{pc.numero_mes}', '').strip()
            if nombre_curso:
                # Buscar o crear el curso con ese nombre
                curso, _ = Curso.objects.get_or_create(nombre=nombre_curso)
                if pc.curso != curso:
                    pc.curso = curso
                    pc.save()
        messages.success(request, 'Malla curricular actualizada correctamente.')
        return redirect('gestion:editar_malla_curricular', programa_id=programa.id_programa)
    return render(request, 'gestion/editar_malla_curricular.html', {
        'programa': programa,
        'malla': malla,
    })

@login_required
@rol_requerido(roles_permitidos=['Admin', 'Ventas'])
def panel_presencial(request):
    # Obtener la modalidad presencial
    try:
        modalidad_presencial = Modalidad.objects.get(nombre_modalidad__iexact='Presencial')
    except Modalidad.DoesNotExist:
        messages.error(request, 'No existe la modalidad presencial configurada.')
        return redirect('gestion:dashboard')

    # Agrupar alumnos por programa académico en modalidad presencial
    matriculas = Matricula.objects.filter(id_modalidad=modalidad_presencial)
    programas = ProgramaAcademico.objects.filter(matricula__in=matriculas).distinct()

    grupos = []
    for programa in programas:
        alumnos = matriculas.filter(id_programa=programa)
        grupos.append({
            'programa': programa,
            'alumnos': alumnos,
        })

    context = {
        'grupos': grupos,
    }
    return render(request, 'gestion/panel_presencial.html', context)

@login_required
@require_permiso_personalizado('asistencia_presencial')
def asistencia_grupal_presencial(request):
    from django import forms
    # Obtener modalidad presencial
    try:
        modalidad_presencial = Modalidad.objects.get(nombre_modalidad__iexact='Presencial')
    except Modalidad.DoesNotExist:
        messages.error(request, 'No existe la modalidad presencial configurada.')
        return redirect('gestion:dashboard')

    # Formulario para seleccionar programa y fecha
    class FiltroGrupoForm(forms.Form):
        programa = forms.ModelChoiceField(queryset=ProgramaAcademico.objects.filter(matricula__id_modalidad=modalidad_presencial).distinct(), label="Programa Académico", required=True)
        fecha_clase = forms.DateField(label="Fecha de Clase", widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    alumnos = None
    grupo_seleccionado = None
    fecha_clase = None
    asistencia_existente = False
    if request.method == 'POST' and 'filtrar_grupo' in request.POST:
        filtro_form = FiltroGrupoForm(request.POST)
        if filtro_form.is_valid():
            grupo_seleccionado = filtro_form.cleaned_data['programa']
            fecha_clase = filtro_form.cleaned_data['fecha_clase']
            alumnos = Matricula.objects.filter(id_programa=grupo_seleccionado, id_modalidad=modalidad_presencial)
            # Verificar si ya existe asistencia para esa fecha y grupo
            asistencia_existente = Asistencia.objects.filter(
                id_matricula__in=alumnos,
                fecha_clase=fecha_clase
            ).exists()
    elif request.method == 'POST' and 'guardar_asistencia' in request.POST:
        # Guardar asistencias grupales
        from datetime import datetime
        grupo_id = request.POST.get('grupo_id')
        fecha_clase = request.POST.get('fecha_clase')
        # Forzar formato YYYY-MM-DD
        if fecha_clase and not isinstance(fecha_clase, (datetime,)):
            try:
                fecha_clase = datetime.strptime(fecha_clase, '%Y-%m-%d').date()
            except ValueError:
                # Intentar parsear otros formatos comunes
                try:
                    fecha_clase = datetime.strptime(fecha_clase, '%B %d, %Y').date()
                except ValueError:
                    messages.error(request, 'Formato de fecha inválido. Use YYYY-MM-DD.')
                    filtro_form = FiltroGrupoForm()
                    return render(request, 'gestion/asistencia_grupal_presencial.html', {'filtro_form': filtro_form})
        grupo_seleccionado = ProgramaAcademico.objects.get(pk=grupo_id)
        alumnos = Matricula.objects.filter(id_programa=grupo_seleccionado, id_modalidad=modalidad_presencial)
        for matricula in alumnos:
            asistio = request.POST.get(f'asistio_{matricula.id_matricula}', 'off') == 'on'
            justificacion = request.POST.get(f'justificacion_{matricula.id_matricula}', '')
            # Evitar duplicados
            asistencia, created = Asistencia.objects.get_or_create(
                id_matricula=matricula,
                fecha_clase=fecha_clase,
                defaults={
                    'asistio': asistio,
                    'justificacion': justificacion,
                    'id_usuario_registro': request.user.usuario,
                }
            )
            if not created:
                asistencia.asistio = asistio
                asistencia.justificacion = justificacion
                asistencia.save()
        messages.success(request, 'Asistencias guardadas correctamente.')
        filtro_form = FiltroGrupoForm(initial={'programa': grupo_seleccionado, 'fecha_clase': fecha_clase})
        asistencia_existente = True
    else:
        filtro_form = FiltroGrupoForm()

    context = {
        'filtro_form': filtro_form,
        'alumnos': alumnos,
        'grupo_seleccionado': grupo_seleccionado,
        'fecha_clase': fecha_clase,
        'asistencia_existente': asistencia_existente,
    }
    return render(request, 'gestion/asistencia_grupal_presencial.html', context)

@login_required
def menu_rol(request):
    rol = request.user.usuario.rol.nombre if hasattr(request.user, 'usuario') else None
    if request.user.is_superuser:
        return redirect('gestion:dashboard')
    if rol == 'Profesor':
        return redirect('gestion:panel_profesor')
    if rol == 'Estudiante':
        return redirect('gestion:panel_estudiante')
    return redirect('gestion:dashboard')

@login_required
@rol_profesor_required
def panel_profesor(request):
    # Solo programas presencial o semi-presencial asignados al profesor
    profesor = request.user.usuario
    programas = [pp.programa for pp in profesor.profesorprograma_set.filter(programa__id_modalidad__nombre_modalidad__in=['Presencial', 'Semi-presencial'])]
    context = {'programas': programas}
    return render(request, 'gestion/panel_profesor.html', context)

@login_required
@rol_estudiante_required
def panel_estudiante(request):
    estudiante = request.user.usuario
    matriculas = estudiante.matriculas_realizadas.select_related('id_programa', 'id_modalidad').all()
    # Para cada matrícula, filtrar notas solo si está al día en pensiones
    notas_por_matricula = {}
    for matricula in matriculas:
        # Verificar pagos
        pagado_hasta = matricula.pago_set.filter(concepto='Pensión').aggregate(models.Max('numero_cuota'))['numero_cuota__max'] or 0
        notas = []
        for nota in matricula.notas.all():
            if nota.periodo_curso and nota.periodo_curso.numero_mes <= pagado_hasta + 1:
                notas.append(nota)
        notas_por_matricula[matricula] = notas
    context = {'matriculas': matriculas, 'notas_por_matricula': notas_por_matricula}
    return render(request, 'gestion/panel_estudiante.html', context)

class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ['sede', 'concepto', 'monto', 'fecha']

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['sede', 'concepto', 'monto', 'fecha']

@login_required
@require_permiso_personalizado('finanzas')
def panel_gestion_finanzas(request):
    sedes = Sede.objects.all()
    sede_id = request.GET.get('sede')
    sede_seleccionada = Sede.objects.filter(id=sede_id).first() if sede_id else None
    ingresos = Ingreso.objects.filter(sede=sede_seleccionada) if sede_seleccionada else Ingreso.objects.all()
    gastos = Gasto.objects.filter(sede=sede_seleccionada) if sede_seleccionada else Gasto.objects.all()

    ingreso_form = IngresoForm()
    gasto_form = GastoForm()
    if request.method == 'POST':
        if 'registrar_ingreso' in request.POST:
            ingreso_form = IngresoForm(request.POST)
            if ingreso_form.is_valid():
                ingreso_form.save()
                messages.success(request, 'Ingreso registrado correctamente.')
                return redirect(request.path + (f'?sede={sede_id}' if sede_id else ''))
        elif 'registrar_gasto' in request.POST:
            gasto_form = GastoForm(request.POST)
            if gasto_form.is_valid():
                gasto_form.save()
                messages.success(request, 'Gasto registrado correctamente.')
                return redirect(request.path + (f'?sede={sede_id}' if sede_id else ''))
        elif 'exportar_csv' in request.POST:
            tipo = request.POST.get('tipo')
            response = csv_export_finanzas(tipo, ingresos, gastos)
            return response

    total_ingresos = sum(i.monto for i in ingresos)
    total_gastos = sum(g.monto for g in gastos)
    context = {
        'sedes': sedes,
        'sede_seleccionada': sede_seleccionada,
        'ingresos': ingresos,
        'gastos': gastos,
        'ingreso_form': ingreso_form,
        'gasto_form': gasto_form,
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
    }
    return render(request, 'gestion/panel_gestion_finanzas.html', context)

def csv_export_finanzas(tipo, ingresos, gastos):
    response = None
    if tipo == 'ingresos':
        response = csv_response('ingresos.csv', ['Fecha', 'Sede', 'Concepto', 'Monto'], [
            [i.fecha, i.sede.nombre, i.concepto, i.monto] for i in ingresos
        ])
    elif tipo == 'gastos':
        response = csv_response('gastos.csv', ['Fecha', 'Sede', 'Concepto', 'Monto'], [
            [g.fecha, g.sede.nombre, g.concepto, g.monto] for g in gastos
        ])
    return response

def csv_response(filename, headers, rows):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return response

@login_required
@require_permiso_personalizado('consulta_sql')
def consulta_sql(request):
    query = request.POST.get('query', '')
    results = None
    columns = None
    error = None
    message = None

    if request.method == 'POST' and query:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)

                # Si es una consulta que devuelve filas (ej. SELECT)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()

                    # --- Lógica de descarga CSV ---
                    if 'download' in request.POST:
                        response = HttpResponse(content_type='text/csv')
                        # Sanitize query for filename
                        safe_filename = "".join([c for c in query[:20] if c.isalpha() or c.isdigit()]).rstrip() or "query"
                        response['Content-Disposition'] = f'attachment; filename="{safe_filename}_results.csv"'
                        
                        writer = csv.writer(response)
                        writer.writerow(columns) # Escribir cabeceras
                        writer.writerows(results) # Escribir datos
                        
                        return response
                else:
                    # Si es un comando como INSERT, UPDATE, DELETE, etc.
                    message = f"Comando ejecutado con éxito. Filas afectadas: {cursor.rowcount}"

        except Exception as e:
            error = f"Error al ejecutar la consulta: {e}"

    context = {
        'query': query,
        'results': results,
        'columns': columns,
        'error': error,
        'message': message,
    }
    return render(request, 'gestion/consulta_sql.html', context)

@login_required
@require_permiso_personalizado('tablas_bd')
def ver_todas_tablas(request):
    """Vista para superusuario que muestra todas las tablas de la base de datos"""
    tablas_info = []
    
    try:
        with connection.cursor() as cursor:
            # Obtener todas las tablas del esquema público
            cursor.execute("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columnas,
                       (SELECT COUNT(*) FROM information_schema.table_constraints 
                        WHERE table_name = t.table_name AND constraint_type = 'PRIMARY KEY') as tiene_pk
                FROM information_schema.tables t
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            tablas = cursor.fetchall()
            
            for tabla in tablas:
                nombre_tabla = tabla[0]
                num_columnas = tabla[1]
                tiene_pk = tabla[2]
                
                # Obtener información de columnas para cada tabla
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position
                """, [nombre_tabla])
                
                columnas = cursor.fetchall()
                
                # Obtener número de registros
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
                    num_registros = cursor.fetchone()[0]
                except:
                    num_registros = "Error"
                
                # Obtener claves foráneas
                cursor.execute("""
                    SELECT 
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = %s
                """, [nombre_tabla])
                
                foreign_keys = cursor.fetchall()
                
                tablas_info.append({
                    'nombre': nombre_tabla,
                    'num_columnas': num_columnas,
                    'num_registros': num_registros,
                    'tiene_pk': tiene_pk > 0,
                    'columnas': columnas,
                    'foreign_keys': foreign_keys
                })
                
    except Exception as e:
        error = f"Error al obtener información de las tablas: {e}"
        tablas_info = []
    
    context = {
        'tablas_info': tablas_info,
        'error': error if 'error' in locals() else None,
    }
    return render(request, 'gestion/ver_todas_tablas.html', context)
