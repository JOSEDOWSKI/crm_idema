from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, connection
from django.contrib import messages
from django.db.models import Count, Sum, Q, F, FloatField, Case, When, Value
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .decorators import rol_requerido
import json
import random
import csv
from datetime import timedelta
from .forms import LeadForm, ConvertirLeadForm, PagoForm, ClienteEditForm, LeadEditForm, InteraccionForm
from .models import (
    Lead, LeadInteresPrograma, Cliente, Matricula, Pago, Usuario,
    MedioContacto, Modalidad, MedioPago, ProgramaAcademico,
    Departamento, Provincia, Distrito
)

# Create your views here.

@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
def listar_leads(request):
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
    with connection.cursor() as cursor:
        cursor.execute(f'''
            SELECT l.id_lead, l.nombre_completo, l.telefono, l.genero, l.fecha_ingreso, l.estado_lead,
                   u.nombre_usuario, m.nombre_medio
            FROM gestion_lead l
            LEFT JOIN gestion_usuario u ON l.id_usuario_atencion = u.id_usuario
            LEFT JOIN gestion_mediocontacto m ON l.id_medio_contacto = m.id_medio_contacto
            ORDER BY {order_by}
        ''')
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
    context = {
        'leads': leads,
        'current_sort': sort_by,
        'current_direction': direction,
    }
    return render(request, 'gestion/listar_leads.html', context)

@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
def detalle_lead(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    interacciones = lead.interacciones.all()
    form = InteraccionForm()

    if request.method == 'POST':
        form = InteraccionForm(request.POST)
        if form.is_valid():
            interaccion = form.save(commit=False)
            interaccion.id_lead = lead
            interaccion.id_usuario = request.user.usuario # Asigna el usuario logueado
            interaccion.save()
            # Cambia el estado del lead a 'Atendido' después de la primera interacción
            if lead.estado_lead == 'Pendiente':
                lead.estado_lead = 'Atendido'
                lead.save()
            messages.success(request, 'Interacción registrada con éxito.')
            return redirect('gestion:detalle_lead', lead_id=lead.id_lead)

    context = {
        'lead': lead,
        'interacciones': interacciones,
        'form': form
    }
    return render(request, 'gestion/detalle_lead.html', context)

@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
def listar_matriculas(request):
    matriculas = Matricula.objects.select_related(
        'id_cliente__id_lead', 
        'id_programa', 
        'id_modalidad'
    ).all().order_by('-fecha_inscripcion')
    return render(request, 'gestion/listar_matriculas.html', {'matriculas': matriculas})

@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
def detalle_matricula(request, matricula_id):
    matricula = get_object_or_404(
        Matricula.objects.select_related('id_cliente__id_lead', 'id_programa'),
        id_matricula=matricula_id
    )
    pagos = Pago.objects.filter(id_matricula=matricula_id).order_by('-fecha_pago')

    if request.method == 'POST':
        form = PagoForm(request.POST)
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
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
@transaction.atomic
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id_cliente=cliente_id)
    lead = cliente.id_lead

    if request.method == 'POST':
        cliente_form = ClienteEditForm(request.POST, request.FILES, instance=cliente)
        lead_form = LeadEditForm(request.POST, instance=lead)
        if cliente_form.is_valid() and lead_form.is_valid():
            cliente_form.save()
            lead_form.save()
            messages.success(request, f'Se ha actualizado la información de {lead.nombre_completo}.')
            return redirect('gestion:listar_matriculas')
    else:
        cliente_form = ClienteEditForm(instance=cliente)
        lead_form = LeadEditForm(instance=lead)

    context = {
        'cliente_form': cliente_form,
        'lead_form': lead_form,
        'cliente': cliente
    }
    return render(request, 'gestion/editar_cliente.html', context)

@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN])
@transaction.atomic
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
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
@transaction.atomic
def convertir_lead_a_cliente(request, lead_id):
    lead = get_object_or_404(Lead, id_lead=lead_id)

    if lead.estado_lead == 'Convertido':
        # Aquí podrías redirigir a una página de error o mostrar un mensaje
        return redirect('gestion:listar_leads')

    if request.method == 'POST':
        form = ConvertirLeadForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear Cliente
            cliente = Cliente.objects.create(
                id_lead=lead,
                dni=form.cleaned_data['dni'],
                email=form.cleaned_data['email'],
                archivo_dni=form.cleaned_data.get('archivo_dni'),
                archivo_partida=form.cleaned_data.get('archivo_partida')
            )

            # Crear Matrícula
            Matricula.objects.create(
                id_cliente=cliente,
                id_programa=form.cleaned_data['programa'],
                id_modalidad=form.cleaned_data['modalidad'],
                observacion=form.cleaned_data['observacion'],
                id_usuario_inscripcion=lead.id_usuario_atencion 
            )

            # Actualizar estado del Lead
            lead.estado_lead = 'Convertido'
            lead.save()

            return redirect('gestion:listar_leads')
    else:
        # Pasa los intereses del lead al formulario
        programas_interes = lead.intereses.all()
        form = ConvertirLeadForm(lead_intereses=programas_interes)

    return render(request, 'gestion/convertir_lead.html', {'form': form, 'lead': lead})

@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
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

            # Redirigir a una página de éxito o a la lista de leads
            return redirect('gestion:listar_leads') # <-- Crearemos esta URL más adelante
    else:
        form = LeadForm()

    return render(request, 'gestion/crear_lead.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.usuario.rol == Usuario.Roles.VENTAS:
        return redirect('gestion:listar_leads')
    context = {}
    rol_usuario = request.user.usuario.rol
    context['rol_usuario'] = rol_usuario
    context['Roles'] = Usuario.Roles
    with connection.cursor() as cursor:
        if rol_usuario in [Usuario.Roles.ADMIN, Usuario.Roles.ANALISTA]:
            cursor.execute("SELECT COUNT(*) FROM gestion_cliente;")
            total_alumnos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM gestion_lead;")
            total_leads = cursor.fetchone()[0]
            now = timezone.now()
            cursor.execute("SELECT COUNT(*) FROM gestion_lead WHERE EXTRACT(YEAR FROM fecha_ingreso) = %s AND EXTRACT(MONTH FROM fecha_ingreso) = %s;", [now.year, now.month])
            leads_este_mes = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM gestion_cliente c JOIN gestion_matricula m ON c.id_cliente = m.id_cliente WHERE EXTRACT(YEAR FROM m.fecha_inscripcion) = %s AND EXTRACT(MONTH FROM m.fecha_inscripcion) = %s;", [now.year, now.month])
            clientes_este_mes = cursor.fetchone()[0]
            context.update({
                'total_alumnos': total_alumnos,
                'total_leads': total_leads,
                'leads_este_mes': leads_este_mes,
                'clientes_este_mes': clientes_este_mes,
            })
        if rol_usuario == Usuario.Roles.ADMIN:
            cursor.execute("SELECT COUNT(*) FROM gestion_matricula;")
            total_matriculas = cursor.fetchone()[0]
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM gestion_pago;")
            monto_recaudado = cursor.fetchone()[0]
            total_leads = context.get('total_leads', 0)
            tasa_conversion = (context.get('total_alumnos', 0) / total_leads) * 100 if total_leads > 0 else 0
            if total_matriculas > 0:
                cursor.execute("SELECT COUNT(*) FROM gestion_matricula WHERE estado = 'Activo';")
                activos = cursor.fetchone()[0]
                tasa_retencion = (activos / total_matriculas) * 100
            else:
                tasa_retencion = 0
            context.update({
                'monto_recaudado': monto_recaudado,
                'tasa_conversion': tasa_conversion,
                'tasa_retencion': tasa_retencion,
            })
        # Puedes agregar más KPIs usando SQL puro aquí
    return render(request, 'gestion/dashboard.html', context)

@require_POST
@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
def actualizar_estado_lead(request, lead_id):
    try:
        lead = get_object_or_404(Lead, pk=lead_id)
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')

        # Obtiene los estados válidos desde el modelo
        estados_validos = [choice[0] for choice in lead.ESTADO_LEAD_CHOICES]

        if nuevo_estado in estados_validos:
            # Prevenir cambiar a 'Convertido' desde aquí
            if nuevo_estado == 'Convertido':
                 return JsonResponse({'status': 'error', 'message': 'La conversión se hace desde el botón "Convertir".'}, status=400)
            
            lead.estado_lead = nuevo_estado
            lead.save()
            return JsonResponse({'status': 'ok', 'nuevo_estado': nuevo_estado})
        else:
            return JsonResponse({'status': 'error', 'message': 'Estado no válido.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_crear_lead(request):
    try:
        data = json.loads(request.body)
        
        # Validación básica de datos
        nombre = data.get('nombre_completo')
        telefono = data.get('telefono')
        
        if not nombre or not telefono:
            return JsonResponse({'status': 'error', 'message': 'Nombre y teléfono son requeridos.'}, status=400)

        # Asignar a un asesor por defecto o de forma aleatoria (se puede mejorar)
        asesor_default = Usuario.objects.filter(rol='Asesor').first()
        if not asesor_default:
             return JsonResponse({'status': 'error', 'message': 'No hay asesores disponibles.'}, status=500)

        # Asignar un medio de contacto por defecto para la API
        medio_contacto, _ = MedioContacto.objects.get_or_create(nombre_medio='Formulario Web')
        distrito_default = Distrito.objects.first() # Simplificación, se puede mejorar
        if not distrito_default:
            return JsonResponse({'status': 'error', 'message': 'No hay distritos configurados.'}, status=500)

        lead = Lead.objects.create(
            nombre_completo=nombre,
            telefono=telefono,
            email=data.get('email', ''), # Opcional
            genero=data.get('genero', 'Otro'),
            estado_lead='Pendiente',
            id_usuario_atencion=asesor_default,
            id_medio_contacto=medio_contacto,
            id_distrito=distrito_default
        )
        
        # Manejar intereses si se envían
        intereses_ids = data.get('intereses', [])
        if intereses_ids:
            programas = ProgramaAcademico.objects.filter(id_programa__in=intereses_ids)
            lead.intereses.set(programas)

        return JsonResponse({'status': 'ok', 'message': 'Lead creado con éxito.', 'lead_id': lead.id_lead})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Error en el formato de los datos (JSON inválido).'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error interno del servidor: {str(e)}'}, status=500)

@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.ANALISTA])
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
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
def exportar_leads_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="listado_leads.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow([
        'Nombre Completo', 'Telefono', 'Email', 'Genero', 'Estado', 
        'Asesor Asignado', 'Medio de Contacto', 'Distrito', 'Fecha de Ingreso'
    ])
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT l.nombre_completo, l.telefono, l.email, l.genero, l.estado_lead, 
                   u.nombre_usuario, m.nombre_medio, d.nombre, l.fecha_ingreso
            FROM gestion_lead l
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
                row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else ''
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
