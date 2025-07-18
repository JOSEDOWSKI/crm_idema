import random
import string
from django.contrib.auth.models import User
from gestion.models import Empleado, Usuario, RolEmpleado

def generar_dni_random():
    return ''.join(random.choices(string.digits, k=8))

def crear_usuarios_empleados():
    for empleado in Empleado.objects.all():
        dni = empleado.dni or generar_dni_random()
        # Verificar si ya existe un usuario Django con ese username
        if User.objects.filter(username=dni).exists():
            continue
        # Rol según el empleado (si tiene relación con Usuario, úsala; si no, asigna uno genérico)
        rol = empleado.usuario.rol if hasattr(empleado, 'usuario') and empleado.usuario else RolEmpleado.objects.first()
        nombre = f"{empleado.nombres} {empleado.apellidos}".strip()
        user = User.objects.create_user(username=dni, password=dni, first_name=nombre)
        usuario = Usuario.objects.create(user_django=user, nombre_usuario=nombre, rol=rol)
        print(f"Usuario creado para empleado {nombre} (DNI: {dni})")

if __name__ == '__main__':
    crear_usuarios_empleados() 