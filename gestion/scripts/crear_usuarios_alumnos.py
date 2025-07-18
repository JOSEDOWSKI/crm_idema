from django.contrib.auth.models import User
from gestion.models import Cliente, Usuario, RolEmpleado

def crear_usuarios_alumnos():
    rol_estudiante, _ = RolEmpleado.objects.get_or_create(nombre='Estudiante')
    for cliente in Cliente.objects.all():
        dni = cliente.dni
        if not dni:
            continue
        # Verificar si ya existe un usuario Django con ese username
        if User.objects.filter(username=dni).exists():
            continue
        # Crear usuario Django
        user = User.objects.create_user(username=dni, password=dni, first_name=cliente.id_lead.nombre_completo)
        # Crear objeto Usuario
        usuario = Usuario.objects.create(user_django=user, nombre_usuario=cliente.id_lead.nombre_completo, rol=rol_estudiante)
        # Vincular usuario a cliente si es necesario (opcional)
        print(f"Usuario creado para alumno {cliente.id_lead.nombre_completo} (DNI: {dni})")

if __name__ == '__main__':
    crear_usuarios_alumnos() 