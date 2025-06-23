from django import forms
from .models import Lead, ProgramaAcademico, Cliente, Matricula, Modalidad, Pago

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
        ]
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'estado_lead': forms.Select(attrs={'class': 'form-control'}),
            'id_distrito': forms.Select(attrs={'class': 'form-control'}),
            'id_medio_contacto': forms.Select(attrs={'class': 'form-control'}),
            'id_usuario_atencion': forms.Select(attrs={'class': 'form-control'}),
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
        }

class ConvertirLeadForm(forms.Form):
    dni = forms.CharField(max_length=8, label="DNI")
    email = forms.EmailField(label="Email")
    programa = forms.ModelChoiceField(
        queryset=ProgramaAcademico.objects.all(),
        label="Programa a Matricular",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    modalidad = forms.ModelChoiceField(
        queryset=Modalidad.objects.all(),
        label="Modalidad de Estudio",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    observacion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Observación (Opcional)"
    )

    def __init__(self, *args, **kwargs):
        lead_intereses = kwargs.pop('lead_intereses', None)
        super().__init__(*args, **kwargs)
        if lead_intereses:
            self.fields['programa'].queryset = lead_intereses

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['concepto', 'monto', 'id_medio_pago', 'numero_cuota', 'descuento_aplicado']
        widgets = {
            'concepto': forms.Select(attrs={'class': 'form-control'}),
            'id_medio_pago': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_cuota': forms.NumberInput(attrs={'class': 'form-control'}),
            'descuento_aplicado': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'concepto': 'Concepto de Pago',
            'monto': 'Monto (S/)',
            'id_medio_pago': 'Medio de Pago',
            'numero_cuota': 'Número de Cuota (si aplica)',
            'descuento_aplicado': 'Descuento Aplicado (S/)',
        }

class ClienteEditForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['dni', 'email']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
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