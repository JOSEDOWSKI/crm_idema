# Código Actual de Observaciones - Rama Master

## 1. Modelo Matricula (gestion/models.py)

```python
class Matricula(models.Model):
    class EstadoMatricula(models.TextChoices):
        ACTIVO = 'Activo', 'Activo'
        RETIRADO = 'Retirado', 'Retirado'
        EGRESADO = 'Egresado', 'Egresado'

    id_matricula = models.AutoField(primary_key=True)
    fecha_inscripcion = models.DateTimeField(default=timezone.now)
    observacion = models.TextField(blank=True, null=True)  # CAMPO DE OBSERVACIÓN
    estado = models.CharField(max_length=20, choices=EstadoMatricula.choices, default=EstadoMatricula.ACTIVO)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    id_programa = models.ForeignKey(ProgramaAcademico, on_delete=models.PROTECT, db_column='id_programa')
    id_modalidad = models.ForeignKey(Modalidad, on_delete=models.PROTECT, db_column='id_modalidad')
    id_usuario_inscripcion = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='matriculas_realizadas', db_column='id_usuario_inscripcion')

    def __str__(self):
        return f"Matrícula de {self.id_cliente} en {self.id_programa}"
```

## 2. Formulario ConvertirLeadForm (gestion/forms.py)

```python
class ConvertirLeadForm(forms.Form):
    dni = forms.CharField(max_length=8, label="DNI")
    email = forms.EmailField(label="Correo Electrónico")
    programa = forms.ModelChoiceField(queryset=ProgramaAcademico.objects.all(), label="Programa de Interés")
    modalidad = forms.ModelChoiceField(queryset=Modalidad.objects.all(), label="Modalidad")
    observacion = forms.CharField(widget=forms.Textarea, required=False, label="Observación")  # CAMPO DE OBSERVACIÓN
    archivo_dni = forms.FileField(required=False, label="Subir DNI (PDF, JPG, PNG)")
    archivo_partida = forms.FileField(required=False, label="Subir Partida de Nacimiento (PDF, JPG, PNG)")

    def __init__(self, *args, **kwargs):
        lead_intereses = kwargs.pop('lead_intereses', None)
        super().__init__(*args, **kwargs)
        if lead_intereses:
            self.fields['programa'].queryset = lead_intereses
```

## 3. Vista convertir_lead_a_cliente (gestion/views.py)

```python
@login_required
@rol_requerido(roles_permitidos=[Usuario.Roles.ADMIN, Usuario.Roles.VENTAS])
@transaction.atomic
def convertir_lead_a_cliente(request, lead_id):
    lead = get_object_or_404(Lead, id_lead=lead_id)

    if lead.estado_lead == 'Convertido':
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
                observacion=form.cleaned_data['observacion'],  # GUARDA LA OBSERVACIÓN
                id_usuario_inscripcion=lead.id_usuario_atencion 
            )

            # Actualizar estado del Lead
            lead.estado_lead = 'Convertido'
            lead.save()

            return redirect('gestion:listar_leads')
    else:
        programas_interes = lead.intereses.all()
        form = ConvertirLeadForm(lead_intereses=programas_interes)

    return render(request, 'gestion/convertir_lead.html', {'form': form, 'lead': lead})
```

## 4. Template convertir_lead.html (gestion/templates/gestion/convertir_lead.html)

```html
<div class="mb-3">
    {{ form.observacion.label_tag }}
    <textarea name="observacion" class="form-control" id="id_observacion" rows="3"></textarea>
</div>
```

## 5. Template detalle_matricula.html (gestion/templates/gestion/detalle_matricula.html)

**NOTA: En el template actual NO se muestra la observación de la matrícula**

```html
<div class="card-body">
    <h5 class="card-title">Información del Alumno</h5>
    <p><strong>Nombre:</strong> {{ matricula.id_cliente.id_lead.nombre_completo }}</p>
    <p><strong>DNI:</strong> {{ matricula.id_cliente.dni }}</p>
    <p><strong>Email:</strong> {{ matricula.id_cliente.email }}</p>
    <p><strong>Programa:</strong> {{ matricula.id_programa.nombre_programa }}</p>
    <p><strong>Modalidad:</strong> {{ matricula.id_modalidad.nombre_modalidad }}</p>
    <p><strong>Estado:</strong> {{ matricula.get_estado_display }}</p>
    <!-- FALTA MOSTRAR LA OBSERVACIÓN -->
</div>
```

## 6. Migración inicial (gestion/migrations/0001_initial.py)

```python
migrations.CreateModel(
    name='Matricula',
    fields=[
        ('id_matricula', models.AutoField(primary_key=True, serialize=False)),
        ('fecha_inscripcion', models.DateTimeField(default=django.utils.timezone.now)),
        ('observacion', models.TextField(blank=True, null=True)),  # CAMPO DE OBSERVACIÓN
        ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Retirado', 'Retirado'), ('Egresado', 'Egresado')], default='Activo', max_length=20)),
        ('id_cliente', models.ForeignKey(db_column='id_cliente', on_delete=django.db.models.deletion.CASCADE, to='gestion.cliente')),
        ('id_modalidad', models.ForeignKey(db_column='id_modalidad', on_delete=django.db.models.deletion.PROTECT, to='gestion.modalidad')),
        ('id_programa', models.ForeignKey(db_column='id_programa', on_delete=django.db.models.deletion.PROTECT, to='gestion.programaacademico')),
        ('id_usuario_inscripcion', models.ForeignKey(db_column='id_usuario_inscripcion', on_delete=django.db.models.deletion.PROTECT, related_name='matriculas_realizadas', to='gestion.usuario')),
    ],
),
```

## Resumen del Estado Actual

✅ **Funciona correctamente:**
- Campo `observacion` en modelo `Matricula`
- Formulario `ConvertirLeadForm` incluye campo observación
- Vista `convertir_lead_a_cliente` guarda la observación
- Template `convertir_lead.html` muestra el campo observación

❌ **Problema identificado:**
- Template `detalle_matricula.html` NO muestra la observación guardada
- Falta agregar: `<p><strong>Observación:</strong> {{ matricula.observacion|linebreaks }}</p>` 