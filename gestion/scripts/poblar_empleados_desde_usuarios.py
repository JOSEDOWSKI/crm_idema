from django.core.management.base import BaseCommand
from gestion.models import Usuario, Empleado

class Command(BaseCommand):
    help = 'Crea fichas de empleado para todos los usuarios que no tengan una.'

    def handle(self, *args, **options):
        creados = 0
        for usuario in Usuario.objects.filter(user_django__isnull=False):
            if not hasattr(usuario, 'empleado'):
                nombres = usuario.nombre_usuario.split(' ')[0]
                apellidos = ' '.join(usuario.nombre_usuario.split(' ')[1:])
                Empleado.objects.create(
                    usuario=usuario,
                    nombres=nombres,
                    apellidos=apellidos,
                    cargo=usuario.get_rol_display(),
                )
                creados += 1
        self.stdout.write(self.style.SUCCESS(f'Se crearon {creados} empleados nuevos.')) 