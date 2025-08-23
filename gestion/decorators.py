from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.shortcuts import redirect
from functools import wraps

def rol_requerido(roles_permitidos=[]):
    """
    Decorador para vistas que requiere que un usuario tenga un rol específico.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('gestion:login')

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            try:
                # Comprobamos si el usuario tiene un perfil de Usuario
                if hasattr(request.user, 'usuario') and request.user.usuario.rol.nombre in roles_permitidos:
                    return view_func(request, *args, **kwargs)
            except AttributeError:
                # El usuario no tiene un perfil de Usuario asociado
                return False

            return redirect(reverse('gestion:no_access'))

        return _wrapped_view

    return decorator

def rol_profesor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or (hasattr(request.user, 'usuario') and request.user.usuario.rol.nombre == 'Profesor'):
            return view_func(request, *args, **kwargs)
        return redirect('gestion:no_access')
    return _wrapped_view

def rol_estudiante_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or (hasattr(request.user, 'usuario') and request.user.usuario.rol.nombre == 'Estudiante'):
            return view_func(request, *args, **kwargs)
        return redirect('gestion:no_access')
    return _wrapped_view 

def require_permiso_personalizado(codigo_permiso):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            usuario = getattr(request.user, 'usuario', None)
            if usuario:
                # Permisos directos
                tiene_permiso_directo = usuario.permisos_personalizados.filter(codigo=codigo_permiso).exists()
                # Permisos por rol
                tiene_permiso_rol = usuario.rol and usuario.rol.permisos.filter(codigo=codigo_permiso).exists()
                if tiene_permiso_directo or tiene_permiso_rol:
                    return view_func(request, *args, **kwargs)
            return redirect('gestion:no_access')
        return _wrapped_view
    return decorator 