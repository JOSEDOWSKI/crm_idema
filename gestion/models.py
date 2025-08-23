from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# ==============================================================
# SECCIÓN 1: MODELOS DE CATÁLOGO Y SOPORTE
# ==============================================================

class RolEmpleado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    permisos = models.ManyToManyField('PermisoPersonalizado', blank=True, related_name='roles_con_permiso')

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    user_django = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    nombre_usuario = models.CharField(max_length=255)
    rol = models.ForeignKey(RolEmpleado, on_delete=models.PROTECT, related_name='usuarios')
    activo = models.BooleanField(default=True)
    permisos_personalizados = models.ManyToManyField('PermisoPersonalizado', blank=True, related_name="usuarios_con_permiso")

    def __str__(self):
        return self.nombre_usuario

    def get_permisos_totales(self):
        permisos_rol = self.rol.permisos.all() if self.rol else PermisoPersonalizado.objects.none()
        permisos_personales = self.permisos_personalizados.all()
        return (permisos_rol | permisos_personales).distinct()

class MedioContacto(models.Model):
    id_medio_contacto = models.AutoField(primary_key=True)
    nombre_medio = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_medio

class Modalidad(models.Model):
    id_modalidad = models.AutoField(primary_key=True)
    nombre_modalidad = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_modalidad

class MedioPago(models.Model):
    id_medio_pago = models.AutoField(primary_key=True)
    nombre_medio = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_medio

# Modificación de ProgramaAcademico para agregar sede
class ProgramaAcademico(models.Model):
    class TipoPrograma(models.TextChoices):
        CURSO = 'Curso', 'Curso'
        ESPECIALIZACION = 'Especialización', 'Especialización'
        CARRERA_TECNICA = 'Carrera Técnica', 'Carrera Técnica'

    id_programa = models.AutoField(primary_key=True)
    nombre_programa = models.CharField(max_length=255)
    tipo_programa = models.CharField(max_length=50, choices=TipoPrograma.choices, default=TipoPrograma.CURSO)
    duracion_meses = models.IntegerField(default=1, verbose_name="Duración en meses")
    numero_pensiones = models.IntegerField(default=1, verbose_name="Número de pensiones")
    precio_matricula = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_pension_virtual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_pension_presencial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_curso_unico = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sede = models.ForeignKey('Sede', on_delete=models.PROTECT, related_name='programas', null=True, blank=True)

    def __str__(self):
        return self.nombre_programa

    def save(self, *args, **kwargs):
        # Calcular automáticamente el número de pensiones según el tipo de programa
        if self.tipo_programa == self.TipoPrograma.CURSO:
            self.duracion_meses = 1
            self.numero_pensiones = 1
        elif self.tipo_programa == self.TipoPrograma.ESPECIALIZACION:
            self.duracion_meses = 10
            self.numero_pensiones = 10
        elif self.tipo_programa == self.TipoPrograma.CARRERA_TECNICA:
            self.duracion_meses = 30
            self.numero_pensiones = 30
        
        super().save(*args, **kwargs)

    @property
    def descripcion_completa(self):
        """Retorna una descripción completa del programa"""
        return f"{self.nombre_programa} - {self.get_tipo_programa_display()} ({self.duracion_meses} meses, {self.numero_pensiones} pensiones)"

# ==============================================================
# SECCIÓN 2: MODELOS GEOGRÁFICOS (UBIGEO)
# ==============================================================

class Departamento(models.Model):
    id_departamento = models.CharField(max_length=2, primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Provincia(models.Model):
    id_provincia = models.CharField(max_length=4, primary_key=True)
    nombre = models.CharField(max_length=100)
    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, db_column='id_departamento')

    def __str__(self):
        return self.nombre

class Distrito(models.Model):
    id_distrito = models.CharField(max_length=6, primary_key=True)
    nombre = models.CharField(max_length=100)
    id_provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, db_column='id_provincia')

    def __str__(self):
        return f"{self.nombre} ({self.id_provincia.nombre})"

# ==============================================================
# SECCIÓN 3: MODELOS CENTRALES (LEAD, CLIENTE, MATRICULA)
# ==============================================================

class Lead(models.Model):
    class Genero(models.TextChoices):
        MASCULINO = 'Masculino', 'Masculino'
        FEMENINO = 'Femenino', 'Femenino'
        OTRO = 'Otro', 'Otro'

    ESTADO_LEAD_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Atendido', 'Atendido'),
        ('No Atendido', 'No Atendido'),
        ('Convertido', 'Convertido'),
    ]

    id_lead = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    nivel_estudios = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=10, choices=Genero.choices)
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    estado_lead = models.CharField(max_length=20, choices=ESTADO_LEAD_CHOICES)
    id_usuario_atencion = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='leads_atendidos', db_column='id_usuario_atencion')
    id_medio_contacto = models.ForeignKey(MedioContacto, on_delete=models.PROTECT, db_column='id_medio_contacto')
    id_distrito = models.ForeignKey(Distrito, on_delete=models.PROTECT, db_column='id_distrito')
    intereses = models.ManyToManyField(ProgramaAcademico, through='LeadInteresPrograma')
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones generales")

    def __str__(self):
        return self.nombre_completo

    def get_estado_lead_choices(self):
        return self.ESTADO_LEAD_CHOICES

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    id_lead = models.OneToOneField(Lead, on_delete=models.CASCADE)
    dni = models.CharField(max_length=8, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    archivo_dni = models.FileField(upload_to='documentos_clientes/', blank=True, null=True, verbose_name="Archivo DNI (PDF o Imagen)")
    archivo_partida = models.FileField(upload_to='documentos_clientes/', blank=True, null=True, verbose_name="Partida de Nacimiento (PDF o Imagen)")

    def __str__(self):
        return self.id_lead.nombre_completo

class Interaccion(models.Model):
    id_interaccion = models.AutoField(primary_key=True)
    id_lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='interacciones')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_interaccion = models.DateTimeField(default=timezone.now)
    tipo_interaccion = models.CharField(max_length=50, choices=[
        ('Llamada', 'Llamada'),
        ('Email', 'Email'),
        ('Reunión', 'Reunión'),
        ('WhatsApp', 'WhatsApp'),
        ('Otro', 'Otro'),
    ])
    resultado = models.TextField()

    class Meta:
        ordering = ['-fecha_interaccion']

    def __str__(self):
        return f"Interacción de {self.id_usuario.nombre_usuario} con {self.id_lead.nombre_completo} el {self.fecha_interaccion.strftime('%d/%m/%Y')}"

class LeadInteresPrograma(models.Model):
    id_lead = models.ForeignKey(Lead, on_delete=models.CASCADE, db_column='id_lead')
    id_programa = models.ForeignKey(ProgramaAcademico, on_delete=models.CASCADE, db_column='id_programa')

    class Meta:
        unique_together = ('id_lead', 'id_programa')
        db_table = 'gestion_lead_interes_programa'

class Matricula(models.Model):
    class EstadoMatricula(models.TextChoices):
        ACTIVO = 'Activo', 'Activo'
        RETIRADO = 'Retirado', 'Retirado'
        EGRESADO = 'Egresado', 'Egresado'

    id_matricula = models.AutoField(primary_key=True)
    fecha_inscripcion = models.DateTimeField(default=timezone.now)
    observacion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=EstadoMatricula.choices, default=EstadoMatricula.ACTIVO)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    id_programa = models.ForeignKey(ProgramaAcademico, on_delete=models.PROTECT, db_column='id_programa')
    id_modalidad = models.ForeignKey(Modalidad, on_delete=models.PROTECT, db_column='id_modalidad')
    id_usuario_inscripcion = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='matriculas_realizadas', db_column='id_usuario_inscripcion')

    def __str__(self):
        return f"Matrícula de {self.id_cliente} en {self.id_programa}"

# ==============================================================
# SECCIÓN 4: MODELO DE PAGOS
# ==============================================================

class Pago(models.Model):
    class ConceptoPago(models.TextChoices):
        MATRICULA = 'Matrícula', 'Matrícula'
        PENSION = 'Pensión', 'Pensión'
        PAGO_UNICO = 'Pago Único', 'Pago Único'

    id_pago = models.AutoField(primary_key=True)
    fecha_pago = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=20, choices=ConceptoPago.choices)
    numero_cuota = models.IntegerField(blank=True, null=True)
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    id_matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, db_column='id_matricula')
    id_medio_pago = models.ForeignKey(MedioPago, on_delete=models.PROTECT, db_column='id_medio_pago')
    archivo_comprobante = models.FileField(upload_to='comprobantes_pagos/', blank=True, null=True, verbose_name="Comprobante de pago (PDF o imagen)")
    sede = models.ForeignKey('Sede', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Sede del ingreso")

    def __str__(self):
        return f"Pago de {self.monto} por {self.concepto} para {self.id_matricula.id_cliente}"

    def save(self, *args, **kwargs):
        # Asignar automáticamente la sede según la modalidad si no está asignada
        if not self.sede:
            self.sede = self.obtener_sede_segun_modalidad()
        
        # Crear registro de ingreso automáticamente
        self.crear_ingreso_automatico()
        
        super().save(*args, **kwargs)

    def obtener_sede_segun_modalidad(self):
        """Determina la sede según la modalidad de la matrícula"""
        try:
            modalidad = self.id_matricula.id_modalidad.nombre_modalidad.lower()
            
            # Si es virtual, asignar a Arequipa Virtual
            if 'virtual' in modalidad:
                return Sede.objects.get(nombre='Arequipa Virtual')
            # Si es presencial o semi-presencial, asignar a Sede Principal Pedregal
            elif 'presencial' in modalidad or 'semi' in modalidad:
                return Sede.objects.get(nombre='Sede Principal Pedregal')
            # Para otros casos, usar la sede del programa
            else:
                return self.id_matricula.id_programa.sede
        except Sede.DoesNotExist:
            # Si no existe la sede específica, usar la sede del programa
            return self.id_matricula.id_programa.sede

    def crear_ingreso_automatico(self):
        """Crea automáticamente un registro de ingreso cuando se guarda un pago"""
        try:
            # Solo crear ingreso si no existe uno para este pago
            if not hasattr(self, 'ingreso_creado') or not self.ingreso_creado:
                sede = self.obtener_sede_segun_modalidad()
                if sede:
                    concepto = f"{self.get_concepto_display()} - {self.id_matricula.id_programa.nombre_programa}"
                    if self.numero_cuota:
                        concepto += f" (Cuota {self.numero_cuota})"
                    
                    Ingreso.objects.create(
                        sede=sede,
                        concepto=concepto,
                        monto=self.monto,
                        fecha=self.fecha_pago.date()
                    )
                    self.ingreso_creado = True
        except Exception as e:
            # Log del error pero no fallar el guardado del pago
            print(f"Error al crear ingreso automático: {e}")

    @property
    def sede_asignada(self):
        """Retorna la sede asignada al pago"""
        return self.sede or self.obtener_sede_segun_modalidad()

# ==============================================================
# SECCIÓN 5: MODELOS DE OBSERVACIONES
# ==============================================================

class ObservacionLead(models.Model):
    id_observacion = models.AutoField(primary_key=True)
    id_lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='observaciones_lead')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuario que registra")
    fecha_observacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de observación")
    observacion = models.TextField(verbose_name="Observación")

    class Meta:
        ordering = ['-fecha_observacion']
        verbose_name = "Observación de Lead"
        verbose_name_plural = "Observaciones de Leads"

    def __str__(self):
        return f"Observación de {self.id_usuario.nombre_usuario} el {self.fecha_observacion.strftime('%d/%m/%Y %H:%M')}"

class ObservacionMatricula(models.Model):
    id_observacion = models.AutoField(primary_key=True)
    id_matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='observaciones_matricula')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuario que registra")
    fecha_observacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de observación")
    observacion = models.TextField(verbose_name="Observación")

    class Meta:
        ordering = ['-fecha_observacion']
        verbose_name = "Observación de Matrícula"
        verbose_name_plural = "Observaciones de Matrículas"

    def __str__(self):
        return f"Observación de {self.id_usuario.nombre_usuario} el {self.fecha_observacion.strftime('%d/%m/%Y %H:%M')}"

# ==============================================================
# SECCIÓN 6: MODELOS ACADÉMICOS (PERÍODOS Y NOTAS)
# ==============================================================

class Curso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class PeriodoCurso(models.Model):
    programa = models.ForeignKey(ProgramaAcademico, on_delete=models.CASCADE, related_name='malla')
    numero_mes = models.IntegerField()
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('programa', 'numero_mes')
        ordering = ['programa', 'numero_mes']

    def __str__(self):
        return f"{self.programa.nombre_programa} - Mes {self.numero_mes}: {self.curso.nombre}"

class Nota(models.Model):
    class TipoNota(models.TextChoices):
        PRACTICA = 'Práctica', 'Práctica'
        TEORICA = 'Teórica', 'Teórica'
        FINAL = 'Final', 'Final'
        RECUPERACION = 'Recuperación', 'Recuperación'

    id_nota = models.AutoField(primary_key=True)
    id_matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='notas', verbose_name="Matrícula")
    periodo_curso = models.ForeignKey(PeriodoCurso, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Curso/Mes")
    tipo_nota = models.CharField(max_length=20, choices=TipoNota.choices, default=TipoNota.FINAL)
    nota = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Nota (0-20)")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Registro")
    id_usuario_registro = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuario que registra")

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        unique_together = ['id_matricula', 'periodo_curso', 'tipo_nota']

    def __str__(self):
        return f"Nota {self.nota} - {self.tipo_nota} - {self.id_matricula} - {self.periodo_curso}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.nota < 0 or self.nota > 20:
            raise ValidationError('La nota debe estar entre 0 y 20')

    @property
    def estado_nota(self):
        if self.nota >= 14:
            return "Aprobado"
        elif self.nota >= 10:
            return "Desaprobado"
        else:
            return "Muy Bajo"

    @property
    def puede_recibir_nota(self):
        # Obtener el número máximo de cuotas pagadas
        max_cuota_pagada = Pago.objects.filter(
            id_matricula=self.id_matricula,
            concepto='Pensión'
        ).aggregate(max_cuota=models.Max('numero_cuota'))['max_cuota'] or 0
        periodo_actual = max_cuota_pagada + 1
        return self.periodo_curso.numero_mes <= periodo_actual if self.periodo_curso else False

class Asistencia(models.Model):
    id_asistencia = models.AutoField(primary_key=True)
    id_matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='asistencias', verbose_name="Matrícula")
    periodo_curso = models.ForeignKey(PeriodoCurso, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Curso/Mes")
    fecha_clase = models.DateField(verbose_name="Fecha de Clase")
    asistio = models.BooleanField(default=True, verbose_name="Asistió")
    justificacion = models.TextField(blank=True, null=True, verbose_name="Justificación")
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Registro")
    id_usuario_registro = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuario que registra")

    class Meta:
        ordering = ['-fecha_clase']
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = ['id_matricula', 'periodo_curso', 'fecha_clase']

    def __str__(self):
        estado = "Asistió" if self.asistio else "Faltó"
        return f"{estado} - {self.id_matricula} - {self.periodo_curso} - {self.fecha_clase}"

    @property
    def porcentaje_asistencia_periodo(self):
        total_clases = Asistencia.objects.filter(
            id_matricula=self.id_matricula,
            periodo_curso=self.periodo_curso
        ).count()
        clases_asistidas = Asistencia.objects.filter(
            id_matricula=self.id_matricula,
            periodo_curso=self.periodo_curso,
            asistio=True
        ).count()
        if total_clases == 0:
            return 0
        return (clases_asistidas / total_clases) * 100

# ==============================================================
# SECCIÓN 7: MODELO DE EMPLEADOS Y PLANILLA
# ==============================================================

class Empleado(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='empleado', verbose_name="Usuario del sistema")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    banco = models.CharField(max_length=100, blank=True)
    cuenta_bancaria = models.CharField(max_length=30, blank=True)
    cci = models.CharField(max_length=30, blank=True)
    cargo = models.CharField(max_length=100)
    fecha_ingreso = models.DateField(null=True, blank=True)
    tipo_contrato = models.CharField(max_length=100, blank=True)
    horas_contrato = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Horas según contrato")
    sueldo_basico = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tasa_afp = models.DecimalField(max_digits=5, decimal_places=4, default=0.10, verbose_name="Tasa AFP (ej: 0.125)")
    sueldo_por_hora = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    horas_extras = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    inasistencias = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    comisiones = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bonos = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    remuneracion_bruta = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    neto_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    neto_quincenal = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    aporte_empleador = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    sede = models.ForeignKey('Sede', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Sede del empleado")

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.usuario})"

# ==============================================================
# SECCIÓN 8: DOCUMENTOS/INFORMES DE EMPLEADOS
# ==============================================================

class Documento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='documentos_empleados/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='documentos')
    # Reseña del admin
    resena_admin = models.TextField(blank=True, null=True)
    fecha_resena = models.DateTimeField(blank=True, null=True)
    usuario_admin_resena = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='resenas_documentos')

    def __str__(self):
        return f"{self.titulo} - {self.empleado.nombres} {self.empleado.apellidos}"

class Sede(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class ProfesorPrograma(models.Model):
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol__nombre': 'Profesor'})
    programa = models.ForeignKey(ProgramaAcademico, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profesor} - {self.programa}"

class Ingreso(models.Model):
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT)
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Ingreso {self.concepto} - {self.sede} - {self.monto}"

class Gasto(models.Model):
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT)
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Gasto {self.concepto} - {self.sede} - {self.monto}"

class PermisoPersonalizado(models.Model):
    CODIGO_VISTA_CHOICES = [
        ("dashboard", "Dashboard"),
        ("leads", "Leads"),
        ("crear_lead", "Crear Lead"),
        ("matriculas", "Matrículas"),
        ("malla_curricular", "Malla Curricular"),
        ("asistencia_presencial", "Asistencia Presencial"),
        ("empleados", "Empleados"),
        ("nuevo_empleado", "Nuevo empleado"),
        ("documentacion", "Documentación"),
        ("consulta_sql", "Consulta SQL"),
        ("tablas_bd", "Tablas BD"),
        ("poblar_bd", "Poblar BD"),
        ("finanzas", "Finanzas"),
    ]
    codigo = models.CharField(max_length=32, choices=CODIGO_VISTA_CHOICES, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class PlanillaEmpleado(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='planillas')
    mes = models.IntegerField()  # 1-12
    anio = models.IntegerField()
    sueldo = models.DecimalField(max_digits=10, decimal_places=2)
    aportes = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    neto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)
    gasto = models.OneToOneField('Gasto', on_delete=models.SET_NULL, null=True, blank=True, related_name='planilla_empleado')

    class Meta:
        unique_together = ('empleado', 'mes', 'anio')
        verbose_name = 'Pago de Planilla'
        verbose_name_plural = 'Pagos de Planilla'

    def __str__(self):
        return f"Planilla {self.empleado} - {self.mes}/{self.anio}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Crear o actualizar el gasto asociado a la sede del empleado
        if self.empleado.sede:
            concepto = f"Planilla {self.empleado.nombres} {self.empleado.apellidos} - {self.mes}/{self.anio}"
            gasto, created = Gasto.objects.get_or_create(
                sede=self.empleado.sede,
                concepto=concepto,
                monto=self.neto_pagado,
                fecha=self.fecha_pago
            )
            self.gasto = gasto
            super().save(update_fields=['gasto'])

