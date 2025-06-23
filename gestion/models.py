from django.db import models
from django.utils import timezone

# ==============================================================
# SECCIÓN 1: MODELOS DE CATÁLOGO Y SOPORTE
# ==============================================================

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=255)
    rol = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_usuario

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

class ProgramaAcademico(models.Model):
    class TipoPrograma(models.TextChoices):
        CARRERA_3_ANOS = 'Carrera 3 años', 'Carrera 3 años'
        CARRERA_1_ANO = 'Carrera 1 año', 'Carrera 1 año'
        CURSO_1_MES = 'Curso 1 mes', 'Curso 1 mes'

    id_programa = models.AutoField(primary_key=True)
    nombre_programa = models.CharField(max_length=255)
    tipo_programa = models.CharField(max_length=50, choices=TipoPrograma.choices)
    precio_matricula = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_pension_virtual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_pension_presencial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_curso_unico = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nombre_programa

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

    def __str__(self):
        return f"Pago de {self.monto} por {self.concepto} para {self.id_matricula.id_cliente}"
