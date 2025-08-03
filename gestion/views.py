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
    
    # Validar parámetros para seguridad
    if sort_by not in valid_sort_fields:
        sort_by = 'fecha_ingreso'
    if direction not in ['asc', 'desc']:
        direction = 'desc'

    # Construir el campo de ordenamiento
    order_by_field = f'-{sort_by}' if direction == 'desc' else sort_by
    
    leads = Lead.objects.select_related('id_usuario_atencion', 'id_medio_contacto').all().order_by(order_by_field)
    
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
    # BORRADO
    Pago.objects.all().delete()
    LeadInteresPrograma.objects.all().delete()
    Matricula.objects.all().delete()
    Cliente.objects.all().delete()
    Lead.objects.all().delete()
    Usuario.objects.all().delete()
    User.objects.filter(is_superuser=False).delete() # Borra usuarios de Django que no son admins
    MedioContacto.objects.all().delete()
    ProgramaAcademico.objects.all().delete()
    Modalidad.objects.all().delete()
    MedioPago.objects.all().delete()
    Distrito.objects.all().delete()
    Provincia.objects.all().delete()
    Departamento.objects.all().delete()

    # --- CREACIÓN DE DATOS DE CATÁLOGO ---
    # Crear usuarios de Django y perfiles de Usuario
    usuarios_data = [
        {'nombre': 'Ana García', 'rol': Usuario.Roles.ADMIN, 'user': 'admin_ana'},
        {'nombre': 'Luis Torres', 'rol': Usuario.Roles.VENTAS, 'user': 'ventas_luis'},
        {'nombre': 'Dayana Solis', 'rol': Usuario.Roles.VENTAS, 'user': 'ventas_dayana'},
        {'nombre': 'Marco Polo', 'rol': Usuario.Roles.MARKETING, 'user': 'mkt_marco'},
        {'nombre': 'Jorge Paz', 'rol': Usuario.Roles.ANALISTA, 'user': 'data_jorge'},
    ]
    asesores = []
    for data in usuarios_data:
        user, created = User.objects.get_or_create(username=data['user'])
        if created:
            user.set_password('123') # Contraseña simple para desarrollo
            user.first_name = data['nombre'].split()[0]
            user.last_name = ' '.join(data['nombre'].split()[1:])
            user.save()
        
        usuario_perfil = Usuario.objects.create(
            user_django=user,
            nombre_usuario=data['nombre'],
            rol=data['rol']
        )
        # Solo los de ventas pueden ser 'asesores' de un lead
        if usuario_perfil.rol == Usuario.Roles.VENTAS or usuario_perfil.rol == Usuario.Roles.ADMIN:
            asesores.append(usuario_perfil)
    
    medios_contacto = [MedioContacto.objects.create(nombre_medio=name) for name in ['Facebook', 'TikTok', 'Página Web', 'Familiar', 'Instagram', 'Contacto Directo']]
    modalidades = [Modalidad.objects.create(nombre_modalidad=name) for name in ['Presencial', 'Virtual', 'Semi-presencial']]
    medios_pago = [MedioPago.objects.create(nombre_medio=name) for name in ['Yape', 'Tarjeta de Crédito', 'Transferencia BCP', 'Efectivo']]
    
    programas = [
        ProgramaAcademico.objects.create(nombre_programa='Diseño Gráfico Digital', tipo_programa='Carrera 3 años', precio_matricula=200.00, precio_pension_presencial=450.00, precio_pension_virtual=350.00),
        ProgramaAcademico.objects.create(nombre_programa='Marketing Digital', tipo_programa='Carrera 1 año', precio_matricula=150.00, precio_pension_presencial=400.00, precio_pension_virtual=300.00),
        ProgramaAcademico.objects.create(nombre_programa='Excel para Negocios', tipo_programa='Curso 1 mes', precio_curso_unico=250.00),
        ProgramaAcademico.objects.create(nombre_programa='Enfermería', tipo_programa='Carrera 3 años', precio_matricula=220.00, precio_pension_presencial=480.00, precio_pension_virtual=380.00),
        ProgramaAcademico.objects.create(nombre_programa='Agropecuaria', tipo_programa='Carrera 3 años', precio_matricula=180.00, precio_pension_presencial=410.00, precio_pension_virtual=310.00),
    ]

    dep_aqp = Departamento.objects.create(id_departamento='04', nombre='AREQUIPA')
    prov_aqp = Provincia.objects.create(id_provincia='0401', nombre='AREQUIPA', id_departamento=dep_aqp)
    distritos_aqp = [Distrito.objects.create(id_distrito=f'0401{i:02d}', nombre=n, id_provincia=prov_aqp) for i, n in enumerate(['AREQUIPA', 'CAYMA', 'YANAHUARA', 'CERRO COLORADO', 'SOCABAYA'], 1)]
    
    dep_lim = Departamento.objects.create(id_departamento='15', nombre='LIMA')
    prov_lim = Provincia.objects.create(id_provincia='1501', nombre='LIMA', id_departamento=dep_lim)
    distritos_lim = [Distrito.objects.create(id_distrito=f'1501{i:02d}', nombre=n, id_provincia=prov_lim) for i, n in enumerate(['LIMA', 'MIRAFLORES', 'SAN ISIDRO', 'LA MOLINA', 'SURCO'], 1)]
    
    todos_distritos = distritos_aqp + distritos_lim
    
    # --- GENERACIÓN DE LEADS Y CLIENTES ---
    nombres = ['Carlos', 'Maria', 'Juan', 'Lucia', 'Pedro', 'Ana', 'Jose', 'Sofia', 'Luis', 'Elena']
    apellidos = ['Quispe', 'Flores', 'Rodriguez', 'García', 'Martinez', 'Perez', 'Gomez', 'Sanchez', 'Diaz', 'Torres']
    
    # Usaremos un set para garantizar nombres únicos y evitar emails duplicados
    nombres_generados = set()
    
    for i in range(40):
        # Generar un nombre único
        nombre = f'{random.choice(nombres)} {random.choice(apellidos)}'
        while nombre in nombres_generados:
             nombre = f'{random.choice(nombres)} {random.choice(apellidos)}'
        nombres_generados.add(nombre)
                
        lead = Lead.objects.create(
            nombre_completo=nombre,
            telefono=f'9{random.randint(10000000, 99999999)}',
            genero=random.choice(['Masculino', 'Femenino']),
            estado_lead='Pendiente', # Empezamos con pendiente
            id_usuario_atencion=random.choice(asesores),
            id_medio_contacto=random.choice(medios_contacto),
            id_distrito=random.choice(todos_distritos),
            fecha_ingreso=timezone.now() - timedelta(days=random.randint(0, 90))
        )
        lead.intereses.set(random.sample(programas, k=random.randint(1, 2)))

        # Decidimos si se convierte o no
        if random.random() < 0.6: # 60% de probabilidad de conversión
            lead.estado_lead = 'Convertido'
            lead.save()
            
            cliente = Cliente.objects.create(
                dni=str(random.randint(10000000, 99999999)),
                email=f'{nombre.replace(" ", ".").lower()}@example.com',
                id_lead=lead
            )
            
            programa_elegido = random.choice(lead.intereses.all())
            modalidad_elegida = random.choice(modalidades)
            
            matricula = Matricula.objects.create(
                id_cliente=cliente,
                id_programa=programa_elegido,
                id_modalidad=modalidad_elegida,
                id_usuario_inscripcion=lead.id_usuario_atencion,
                estado='Activo',
                fecha_inscripcion=lead.fecha_ingreso + timedelta(days=random.randint(1, 10))
            )
            
            # Pagos
            if programa_elegido.tipo_programa == 'Curso 1 mes':
                Pago.objects.create(id_matricula=matricula, monto=programa_elegido.precio_curso_unico, concepto='Pago Único', id_medio_pago=random.choice(medios_pago))
            else:
                Pago.objects.create(id_matricula=matricula, monto=programa_elegido.precio_matricula, concepto='Matrícula', id_medio_pago=random.choice(medios_pago))
                # Pagamos algunas pensiones
                for j in range(random.randint(1, 5)):
                    precio_pension = programa_elegido.precio_pension_presencial if modalidad_elegida.nombre_modalidad == 'Presencial' else programa_elegido.precio_pension_virtual
                    Pago.objects.create(id_matricula=matricula, monto=precio_pension, concepto='Pensión', numero_cuota=j+1, id_medio_pago=random.choice(medios_pago))
        else:
            lead.estado_lead = random.choice(['Atendido', 'No Atendido', 'Pendiente'])
            lead.save()
            
    messages.success(request, 'La base de datos ha sido reiniciada con usuarios, roles y datos de ejemplo.')
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
    # Redirección para el rol de Ventas
    if request.user.usuario.rol == Usuario.Roles.VENTAS:
        return redirect('gestion:listar_leads')

    context = {}
    rol_usuario = request.user.usuario.rol
    context['rol_usuario'] = rol_usuario
    context['Roles'] = Usuario.Roles

    # --- KPIs para ADMIN y ANALISTA ---
    if rol_usuario in [Usuario.Roles.ADMIN, Usuario.Roles.ANALISTA]:
        total_alumnos = Cliente.objects.count()
        total_leads = Lead.objects.count()
        
        now = timezone.now()
        leads_este_mes = Lead.objects.filter(
            fecha_ingreso__year=now.year,
            fecha_ingreso__month=now.month
        ).count()
        
        clientes_este_mes = Cliente.objects.filter(
            matricula__fecha_inscripcion__year=now.year,
            matricula__fecha_inscripcion__month=now.month
        ).count()
        
        context.update({
            'total_alumnos': total_alumnos,
            'total_leads': total_leads,
            'leads_este_mes': leads_este_mes,
            'clientes_este_mes': clientes_este_mes,
        })

    # --- KPIs para ADMIN ---
    if rol_usuario == Usuario.Roles.ADMIN:
        total_matriculas = Matricula.objects.count()
        monto_recaudado = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0
        
        if total_leads > 0:
            tasa_conversion = (context.get('total_alumnos', 0) / total_leads) * 100
        else:
            tasa_conversion = 0

        if total_matriculas > 0:
            activos = Matricula.objects.filter(estado='Activo').count()
            tasa_retencion = (activos / total_matriculas) * 100
        else:
            tasa_retencion = 0

        context.update({
            'monto_recaudado': monto_recaudado,
            'tasa_conversion': tasa_conversion,
            'tasa_retencion': tasa_retencion,
            'conversiones_por_asesor': Usuario.objects.filter(rol=Usuario.Roles.VENTAS).annotate(
                total_leads=Count('leads_atendidos', distinct=True),
                conversiones_totales=Count(
                    'leads_atendidos',
                    filter=Q(leads_atendidos__estado_lead='Convertido'),
                    distinct=True
                )
            ).annotate(
                tasa_conversion_final=Case(
                    When(total_leads=0, then=Value(0.0)),
                    default=(F('conversiones_totales') * 100.0 / F('total_leads')),
                    output_field=FloatField()
                )
            ).order_by('-conversiones_totales'),
            'ingresos_por_programa': ProgramaAcademico.objects.annotate(
                total_recaudado=Sum('matricula__pago__monto')
            ).order_by('-total_recaudado'),
        })

    # --- KPIs para MARKETING y ADMIN ---
    if rol_usuario in [Usuario.Roles.MARKETING, Usuario.Roles.ADMIN]:
        context.update({
            'leads_por_canal': MedioContacto.objects.annotate(
                num_leads=Count('lead')
            ).order_by('-num_leads'),
            'programas_populares': ProgramaAcademico.objects.annotate(
                num_interesados=Count('leadinteresprograma')
            ).order_by('-num_interesados').filter(num_interesados__gt=0),
            'alumnos_por_depto': Departamento.objects.annotate(
                num_alumnos=Count('provincia__distrito__lead__cliente')
            ).order_by('-num_alumnos').filter(num_alumnos__gt=0),
        })

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

    if request.method == 'POST':
        # Medida de seguridad básica: solo permitir consultas SELECT.
        if query.strip().upper().startswith('SELECT'):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()
                
                # --- Lógica de descarga ---
                if 'download' in request.POST:
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="query_results.csv"'
                    
                    writer = csv.writer(response)
                    writer.writerow(columns) # Escribir cabeceras
                    writer.writerows(results) # Escribir datos
                    
                    return response

            except Exception as e:
                error = f"Error al ejecutar la consulta: {e}"
        else:
            error = "Error: Solo se permiten consultas SELECT."

    context = {
        'query': query,
        'results': results,
        'columns': columns,
        'error': error,
    }
    return render(request, 'gestion/consulta_sql.html', context)

@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
def exportar_leads_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="listado_leads.csv"'
    response.write(u'\ufeff'.encode('utf8')) # BOM para manejar carácteres especiales

    writer = csv.writer(response)
    
    # Escribir la fila de la cabecera
    writer.writerow([
        'Nombre Completo', 'Telefono', 'Email', 'Genero', 'Estado', 
        'Asesor Asignado', 'Medio de Contacto', 'Distrito', 'Fecha de Ingreso'
    ])

    # Escribir las filas de datos
    leads = Lead.objects.select_related(
        'id_usuario_atencion', 'id_medio_contacto', 'id_distrito__id_provincia__id_departamento'
    ).all()
    
    for lead in leads:
        writer.writerow([
            lead.nombre_completo,
            lead.telefono,
            lead.cliente.email if hasattr(lead, 'cliente') and lead.cliente else 'No convertido',
            lead.get_genero_display(),
            lead.get_estado_lead_display(),
            lead.id_usuario_atencion.nombre_usuario if lead.id_usuario_atencion else 'N/A',
            lead.id_medio_contacto.nombre_medio if lead.id_medio_contacto else 'N/A',
            lead.id_distrito.nombre if lead.id_distrito else 'N/A',
            lead.fecha_ingreso.strftime('%Y-%m-%d %H:%M:%S')
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
