from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Usuario, RolEmpleado

@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea un perfil de Usuario automáticamente cuando se crea un nuevo User de Django.
    También se asegura de que el nombre de usuario de nuestro perfil se sincronice.
    """
    if created:
        # Obtener o crear un rol por defecto
        rol = RolEmpleado.objects.first()
        if not rol:
            rol = RolEmpleado.objects.create(nombre='Usuario', descripcion='Rol por defecto para usuarios')
        
        Usuario.objects.create(
            user_django=instance, 
            nombre_usuario=instance.get_full_name() or instance.username,
            rol=rol
        )
    else:
        # Si el usuario de Django se actualiza, actualizamos nuestro perfil
        try:
            instance.usuario.nombre_usuario = instance.get_full_name() or instance.username
            instance.usuario.save()
        except Usuario.DoesNotExist:
            # Si por alguna razón el perfil no existe, lo creamos
            rol = RolEmpleado.objects.first()
            if not rol:
                rol = RolEmpleado.objects.create(nombre='Usuario', descripcion='Rol por defecto para usuarios')
            
            Usuario.objects.create(
                user_django=instance, 
                nombre_usuario=instance.get_full_name() or instance.username,
                rol=rol
            ) 