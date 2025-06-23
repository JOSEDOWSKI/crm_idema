from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, connection
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json
import random
from datetime import timedelta
from .forms import LeadForm, ConvertirLeadForm, PagoForm, ClienteEditForm, LeadEditForm
from .models import (
    Lead, LeadInteresPrograma, Cliente, Matricula, Pago, Usuario,
    MedioContacto, Modalidad, MedioPago, ProgramaAcademico,
    Departamento, Provincia, Distrito
)

# Create your views here.

def listar_leads(request):
    leads = Lead.objects.all().order_by('-fecha_ingreso')
    return render(request, 'gestion/listar_leads.html', {'leads': leads})

def listar_matriculas(request):
    matriculas = Matricula.objects.select_related(
        'id_cliente__id_lead', 
        'id_programa', 
        'id_modalidad'
    ).all().order_by('-fecha_inscripcion')
    return render(request, 'gestion/listar_matriculas.html', {'matriculas': matriculas})

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

@transaction.atomic
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id_cliente=cliente_id)
    lead = cliente.id_lead

    if request.method == 'POST':
        cliente_form = ClienteEditForm(request.POST, instance=cliente)
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

@transaction.atomic
def poblar_bd_ejemplo(request):
    # BORRADO
    Pago.objects.all().delete()
    LeadInteresPrograma.objects.all().delete()
    Matricula.objects.all().delete()
    Cliente.objects.all().delete()
    Lead.objects.all().delete()
    Usuario.objects.all().delete()
    MedioContacto.objects.all().delete()
    ProgramaAcademico.objects.all().delete()
    Modalidad.objects.all().delete()
    MedioPago.objects.all().delete()
    Distrito.objects.all().delete()
    Provincia.objects.all().delete()
    Departamento.objects.all().delete()

    # --- CREACIÓN DE DATOS DE CATÁLOGO ---
    asesores = [Usuario.objects.create(nombre_usuario=name, rol='Asesor') for name in ['Ana García', 'Luis Torres', 'Dayana', 'Malu', 'Jorge Paz']]
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
            
    messages.success(request, 'La base de datos ha sido reiniciada con un set de datos de ejemplo ampliado.')
    return redirect('gestion:dashboard')

@transaction.atomic
def convertir_lead_a_cliente(request, lead_id):
    lead = get_object_or_404(Lead, id_lead=lead_id)

    if lead.estado_lead == 'Convertido':
        # Aquí podrías redirigir a una página de error o mostrar un mensaje
        return redirect('gestion:listar_leads')

    if request.method == 'POST':
        form = ConvertirLeadForm(request.POST)
        if form.is_valid():
            # Crear Cliente
            cliente = Cliente.objects.create(
                id_lead=lead,
                dni=form.cleaned_data['dni'],
                email=form.cleaned_data['email']
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

def dashboard(request):
    total_alumnos = Cliente.objects.count()
    total_leads = Lead.objects.count()
    total_matriculas = Matricula.objects.count()

    monto_recaudado = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0

    if total_leads > 0:
        tasa_conversion = (total_alumnos / total_leads) * 100
    else:
        tasa_conversion = 0

    if total_matriculas > 0:
        activos = Matricula.objects.filter(estado='Activo').count()
        tasa_retencion = (activos / total_matriculas) * 100
    else:
        tasa_retencion = 0
    
    # NUEVOS KPIs
    leads_por_canal = MedioContacto.objects.annotate(
        num_leads=Count('lead')
    ).order_by('-num_leads')

    conversiones_por_asesor = Usuario.objects.annotate(
        num_conversiones=Count('leads_atendidos', filter=Q(leads_atendidos__estado_lead='Convertido'))
    ).order_by('-num_conversiones')

    ingresos_por_programa = ProgramaAcademico.objects.annotate(
        total_recaudado=Sum('matricula__pago__monto')
    ).order_by('-total_recaudado')

    programas_populares = ProgramaAcademico.objects.annotate(
        num_inscritos=Count('matricula')
    ).order_by('-num_inscritos').filter(num_inscritos__gt=0)

    alumnos_por_depto = Departamento.objects.annotate(
        num_alumnos=Count('provincia__distrito__lead__cliente')
    ).order_by('-num_alumnos').filter(num_alumnos__gt=0)

    # --- PREPARACIÓN DE DATOS PARA GRÁFICOS ---
    
    # Gráfico 1: Leads por Canal de Marketing
    leads_canal_data = {
        "labels": [item.nombre_medio for item in leads_por_canal],
        "data": [item.num_leads for item in leads_por_canal],
    }

    # Gráfico 2: Conversiones por Asesor
    conversiones_asesor_data = {
        "labels": [item.nombre_usuario for item in conversiones_por_asesor],
        "data": [item.num_conversiones for item in conversiones_por_asesor],
    }
    
    # Gráfico 3: Ingresos por Programa
    ingresos_programa_data = {
        "labels": [item.nombre_programa for item in ingresos_por_programa if item.total_recaudado is not None],
        "data": [float(item.total_recaudado) for item in ingresos_por_programa if item.total_recaudado is not None],
    }

    context = {
        'total_alumnos': total_alumnos,
        'monto_recaudado': monto_recaudado,
        'tasa_conversion': tasa_conversion,
        'tasa_retencion': tasa_retencion,
        'programas_populares': programas_populares,
        'alumnos_por_depto': alumnos_por_depto,
        # Pasando datos para gráficos (además de los datos tabulares)
        'leads_por_canal': leads_por_canal,
        'conversiones_por_asesor': conversiones_por_asesor,
        'ingresos_por_programa': ingresos_por_programa,
        'leads_canal_data_json': json.dumps(leads_canal_data, cls=DjangoJSONEncoder),
        'conversiones_asesor_data_json': json.dumps(conversiones_asesor_data, cls=DjangoJSONEncoder),
        'ingresos_programa_data_json': json.dumps(ingresos_programa_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'gestion/dashboard.html', context)

def consulta_sql(request):
    query = ""
    results = None
    columns = None
    error = None

    if request.method == 'POST':
        query = request.POST.get('query', '')
        # Medida de seguridad básica: solo permitir consultas SELECT.
        if query.strip().upper().startswith('SELECT'):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()
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
