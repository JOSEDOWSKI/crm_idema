from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def rol_requerido(roles_permitidos=[]):
    """
    Decorador para vistas que requiere que un usuario tenga un rol específico.
    """
    def check_roles(user):
        # El superusuario siempre tiene acceso
        if user.is_superuser:
            return True
        # Comprueba si el perfil de usuario tiene uno de los roles permitidos
        try:
            # Asumimos que el OneToOneField se llama 'usuario' en el modelo User
            return user.usuario.rol in roles_permitidos
        except AttributeError:
            # El usuario no tiene un perfil de Usuario asociado
            return False

    return user_passes_test(check_roles) 