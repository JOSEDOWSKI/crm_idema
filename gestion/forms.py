from django import forms
from .models import Lead, ProgramaAcademico, Cliente, Matricula, Modalidad, Pago, Interaccion, ObservacionLead, ObservacionMatricula, PeriodoAcademico, Nota, Asistencia

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

class PeriodoAcademicoForm(forms.ModelForm):
    class Meta:
        model = PeriodoAcademico
        fields = ['numero_periodo', 'nombre_periodo', 'activo']
        widgets = {
            'numero_periodo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Ej: 1, 2, 3, 4...'
            }),
            'nombre_periodo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Período 1, Primer Bimestre...'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'numero_periodo': 'Número de Período',
            'nombre_periodo': 'Nombre del Período (Opcional)',
            'activo': 'Período Activo',
        }

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['id_periodo', 'tipo_nota', 'nota', 'observaciones']
        widgets = {
            'id_periodo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_nota': forms.Select(attrs={'class': 'form-control'}),
            'nota': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20',
                'step': '0.01',
                'placeholder': '0.00 - 20.00'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre la nota...'
            }),
        }
        labels = {
            'id_periodo': 'Período Académico',
            'tipo_nota': 'Tipo de Nota',
            'nota': 'Nota (0-20)',
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
        fields = ['id_periodo', 'fecha_clase', 'asistio', 'justificacion']
        widgets = {
            'id_periodo': forms.Select(attrs={'class': 'form-control'}),
            'fecha_clase': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'asistio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justificacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Justificación de la falta (opcional)...'
            }),
        }
        labels = {
            'id_periodo': 'Período Académico',
            'fecha_clase': 'Fecha de Clase',
            'asistio': 'Asistió',
            'justificacion': 'Justificación',
        } 