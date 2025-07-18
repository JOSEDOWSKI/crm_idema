from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('gestion', '0022_delete_periodoacademico'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sede',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='programaacademico',
            name='sede',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='programas', to='gestion.sede'),
        ),
        migrations.CreateModel(
            name='ProfesorPrograma',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('profesor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.usuario', limit_choices_to={'rol__nombre': 'Profesor'})),
                ('programa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.programaacademico')),
            ],
        ),
        migrations.CreateModel(
            name='Ingreso',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('concepto', models.CharField(max_length=255)),
                ('monto', models.DecimalField(max_digits=10, decimal_places=2)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('sede', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.sede')),
            ],
        ),
        migrations.CreateModel(
            name='Gasto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('concepto', models.CharField(max_length=255)),
                ('monto', models.DecimalField(max_digits=10, decimal_places=2)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('sede', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.sede')),
            ],
        ),
    ] 