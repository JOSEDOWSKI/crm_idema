from django import forms
from django.contrib.auth.models import User
from .models import Lead, ProgramaAcademico, Cliente, Matricula, Modalidad, Pago, Interaccion, ObservacionLead, ObservacionMatricula, Nota, Asistencia, Empleado, Usuario, Documento, RolEmpleado, PermisoPersonalizado
from decimal import Decimal
from .models import Sede

class LeadForm(forms.ModelForm):
    intereses = forms.ModelMultipleChoiceField(
        queryset=ProgramaAcademico.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Carreras/Cursos de Interés"
    )

    class Meta:
        model = Lead
        fields = [
            'nombre_completo',
            'telefono',
            'nivel_estudios',
            'genero',
            'id_distrito',
            'id_medio_contacto',
            'id_usuario_atencion',
            'intereses',
            'estado_lead',
            'observaciones',
        ]
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'estado_lead': forms.Select(attrs={'class': 'form-control'}),
            'id_distrito': forms.Select(attrs={'class': 'form-control'}),
            'id_medio_contacto': forms.Select(attrs={'class': 'form-control'}),
            'id_usuario_atencion': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'telefono': 'Teléfono (Opcional)',
            'nivel_estudios': 'Nivel de Estudios (Opcional)',
            'genero': 'Género',
            'id_distrito': 'Distrito de Residencia',
            'id_medio_contacto': '¿Cómo nos encontró?',
            'id_usuario_atencion': 'Asesor que atiende',
            'estado_lead': 'Estado del Lead',
            'observaciones': 'Observaciones generales',
        }

class ConvertirLeadForm(forms.Form):
    dni = forms.CharField(max_length=8, label="DNI")
    email = forms.EmailField(label="Correo Electrónico")
    sede = forms.ModelChoiceField(queryset=Sede.objects.all(), label="Sede")
    programa = forms.ModelChoiceField(queryset=ProgramaAcademico.objects.all(), label="Programa de Interés")
    modalidad = forms.ModelChoiceField(queryset=Modalidad.objects.all(), label="Modalidad")
    observacion = forms.CharField(widget=forms.Textarea, required=False, label="Observación")
    archivo_dni = forms.FileField(required=False, label="Subir DNI (PDF, JPG, PNG)")
    archivo_partida = forms.FileField(required=False, label="Subir Partida de Nacimiento (PDF, JPG, PNG)")

    def __init__(self, *args, **kwargs):
        lead_intereses = kwargs.pop('lead_intereses', None)
        super().__init__(*args, **kwargs)
        if lead_intereses:
            self.fields['programa'].queryset = lead_intereses

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['concepto', 'monto', 'id_medio_pago', 'numero_cuota', 'descuento_aplicado', 'archivo_comprobante']
        widgets = {
            'concepto': forms.Select(attrs={'class': 'form-control'}),
            'id_medio_pago': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_cuota': forms.NumberInput(attrs={'class': 'form-control'}),
            'descuento_aplicado': forms.NumberInput(attrs={'class': 'form-control'}),
            'archivo_comprobante': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'concepto': 'Concepto de Pago',
            'monto': 'Monto (S/)',
            'id_medio_pago': 'Medio de Pago',
            'numero_cuota': 'Número de Cuota (si aplica)',
            'descuento_aplicado': 'Descuento Aplicado (S/)',
            'archivo_comprobante': 'Adjuntar Comprobante (PDF, JPG, PNG)',
        }

class ClienteEditForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['dni', 'email', 'archivo_dni', 'archivo_partida']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'archivo_dni': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'archivo_partida': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class InteraccionForm(forms.ModelForm):
    class Meta:
        model = Interaccion
        fields = ['tipo_interaccion', 'resultado']
        widgets = {
            'tipo_interaccion': forms.Select(attrs={'class': 'form-control'}),
            'resultado': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LeadEditForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['nombre_completo', 'telefono', 'nivel_estudios', 'genero', 'id_distrito']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel_estudios': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'id_distrito': forms.Select(attrs={'class': 'form-control'}),
        }

class ObservacionLeadForm(forms.ModelForm):
    class Meta:
        model = ObservacionLead
        fields = ['observacion']
        widgets = {
            'observacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe aquí tu observación sobre el lead...'
            }),
        }
        labels = {
            'observacion': 'Nueva observación',
        }

class ObservacionMatriculaForm(forms.ModelForm):
    class Meta:
        model = ObservacionMatricula
        fields = ['observacion']
        widgets = {
            'observacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe aquí tu observación sobre la matrícula...'
            }),
        }
        labels = {
            'observacion': 'Nueva observación',
        }

class MatriculaEditForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['estado', 'observacion']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'estado': 'Estado de la Matrícula',
            'observacion': 'Observaciones',
        }

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['periodo_curso', 'tipo_nota', 'nota', 'observaciones']
        widgets = {
            'periodo_curso': forms.Select(attrs={'class': 'form-control'}),
            'tipo_nota': forms.Select(attrs={'class': 'form-control'}),
            'nota': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'periodo_curso': 'Curso/Mes',
            'tipo_nota': 'Tipo de Nota',
            'nota': 'Nota',
            'observaciones': 'Observaciones',
        }

    def clean_nota(self):
        nota = self.cleaned_data.get('nota')
        if nota is not None:
            if nota < 0 or nota > 20:
                raise forms.ValidationError('La nota debe estar entre 0 y 20')
        return nota

class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['periodo_curso', 'fecha_clase', 'asistio', 'justificacion']
        widgets = {
            'periodo_curso': forms.Select(attrs={'class': 'form-control'}),
            'fecha_clase': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'asistio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justificacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'periodo_curso': 'Curso/Mes',
            'fecha_clase': 'Fecha de Clase',
            'asistio': 'Asistió',
            'justificacion': 'Justificación',
        }

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'nombres', 'apellidos', 'dni', 'fecha_nacimiento', 
            'direccion', 'telefono', 'email', 'banco', 'cuenta_bancaria', 'cci',
            'cargo', 'fecha_ingreso', 'tipo_contrato', 'sede',
            'horas_contrato', 'sueldo_basico', 'sueldo_por_hora',
            'horas_extras', 'inasistencias', 'comisiones', 'bonos', 'descuentos'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '8'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'cuenta_bancaria': forms.TextInput(attrs={'class': 'form-control'}),
            'cci': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Seleccione tipo de contrato'),
                ('Indefinido', 'Indefinido'),
                ('A plazo fijo', 'A plazo fijo'),
                ('Por obra o servicio', 'Por obra o servicio'),
                ('A tiempo parcial', 'A tiempo parcial'),
                ('Otro', 'Otro')
            ]),
            'sede': forms.Select(attrs={'class': 'form-control'}),
            'horas_contrato': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'sueldo_basico': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sueldo_por_hora': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'horas_extras': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'inasistencias': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'comisiones': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descuentos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'dni': 'DNI',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'banco': 'Banco',
            'cuenta_bancaria': 'Cuenta Bancaria',
            'cci': 'CCI',
            'cargo': 'Cargo',
            'fecha_ingreso': 'Fecha de Ingreso',
            'tipo_contrato': 'Tipo de Contrato',
            'sede': 'Sede',
            'horas_contrato': 'Horas según Contrato',
            'sueldo_basico': 'Sueldo Básico (S/)',
            'sueldo_por_hora': 'Sueldo por Hora (S/)',
            'horas_extras': 'Horas Extras',
            'inasistencias': 'Inasistencias (horas)',
            'comisiones': 'Comisiones (S/)',
            'bonos': 'Bonos (S/)',
            'descuentos': 'Descuentos (S/)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer algunos campos opcionales
        for field in ['fecha_nacimiento', 'direccion', 'telefono', 'banco', 
                     'cuenta_bancaria', 'cci', 'fecha_ingreso', 'tipo_contrato', 
                     'sede', 'horas_contrato', 'sueldo_por_hora', 'horas_extras', 
                     'inasistencias', 'comisiones', 'bonos', 'descuentos']:
            self.fields[field].required = False

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni and len(dni) != 8:
            raise forms.ValidationError('El DNI debe tener exactamente 8 dígitos.')
        return dni

    def save(self, commit=True):
        empleado = super().save(commit=False)
        empleado = self.calcular_remuneracion(empleado)
        # No guardar aún, la vista se encargará de crear el usuario y asignarlo
        if commit:
            empleado.save()
        return empleado

    def calcular_remuneracion(self, empleado):
        """Calcula automáticamente la remuneración bruta y neta"""
        sueldo_basico = empleado.sueldo_basico or Decimal('0')
        sueldo_por_hora = empleado.sueldo_por_hora or Decimal('0')
        horas_extras = empleado.horas_extras or Decimal('0')
        inasistencias = empleado.inasistencias or Decimal('0')
        comisiones = empleado.comisiones or Decimal('0')
        bonos = empleado.bonos or Decimal('0')
        descuentos = empleado.descuentos or Decimal('0')

        # Calcular remuneración bruta
        remuneracion_bruta = sueldo_basico
        
        # Agregar pago por horas extras
        if sueldo_por_hora > 0 and horas_extras > 0:
            remuneracion_bruta += (sueldo_por_hora * horas_extras * Decimal('1.5'))
        
        # Descontar inasistencias
        if sueldo_por_hora > 0 and inasistencias > 0:
            remuneracion_bruta -= (sueldo_por_hora * inasistencias)
        
        # Agregar comisiones y bonos
        remuneracion_bruta += comisiones + bonos
        
        # Calcular descuentos legales
        descuento_afp = sueldo_basico * Decimal('0.10')  # AFP 10%
        descuento_salud = sueldo_basico * Decimal('0.09')  # Seguro 9%
        total_descuentos = descuento_afp + descuento_salud + descuentos
        
        # Calcular neto
        neto_mensual = remuneracion_bruta - total_descuentos
        neto_quincenal = neto_mensual / Decimal('2')
        aporte_empleador = sueldo_basico * Decimal('0.20')  # 20% empleador
        
        # Asignar valores
        empleado.remuneracion_bruta = remuneracion_bruta
        empleado.neto_mensual = neto_mensual
        empleado.neto_quincenal = neto_quincenal
        empleado.aporte_empleador = aporte_empleador
        
        return empleado

class EmpleadoConAccesoForm(forms.Form):
    username = forms.CharField(max_length=150, label="Usuario (login)")
    email = forms.EmailField(label="Email")
    rol = forms.ModelChoiceField(queryset=RolEmpleado.objects.all(), label="Rol")
    nombres = forms.CharField(max_length=100, label="Nombres")
    apellidos = forms.CharField(max_length=100, label="Apellidos")
    dni = forms.CharField(max_length=8, label="DNI")
    cargo = forms.CharField(max_length=100, label="Cargo")
    fecha_nacimiento = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    direccion = forms.CharField(max_length=255, required=False, label="Dirección")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono")
    banco = forms.CharField(max_length=100, required=False, label="Banco")
    cuenta_bancaria = forms.CharField(max_length=30, required=False, label="Cuenta Bancaria")
    cci = forms.CharField(max_length=30, required=False, label="CCI")
    fecha_ingreso = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    tipo_contrato = forms.CharField(max_length=100, required=False, label="Tipo de Contrato")
    horas_contrato = forms.DecimalField(max_digits=5, decimal_places=2, required=False, label="Horas según contrato")
    sueldo_basico = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Sueldo Básico")
    sueldo_por_hora = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Sueldo por Hora")
    horas_extras = forms.DecimalField(max_digits=5, decimal_places=2, required=False, label="Horas Extras")
    inasistencias = forms.DecimalField(max_digits=5, decimal_places=2, required=False, label="Inasistencias")
    comisiones = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Comisiones")
    bonos = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Bonos")
    descuentos = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Descuentos")
    remuneracion_bruta = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Remuneración Bruta")
    neto_mensual = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Neto Mensual")
    neto_quincenal = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Neto Quincenal")
    aporte_empleador = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Aporte del Empleador")
    permisos = forms.ModelMultipleChoiceField(
        queryset=PermisoPersonalizado.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permisos de acceso (vistas)"
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ya existe un usuario con ese nombre de usuario.')
        return username
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con ese email.')
        return email
    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if Empleado.objects.filter(dni=dni).exists():
            raise forms.ValidationError('Ya existe un empleado con ese DNI.')
        return dni

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        } 