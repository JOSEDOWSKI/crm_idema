from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Usuario,
    MedioContacto,
    Modalidad,
    MedioPago,
    ProgramaAcademico,
    Departamento,
    Provincia,
    Distrito,
    Lead,
    Cliente,
    LeadInteresPrograma,
    Matricula,
    Pago,
)

# Define un 'inline' para el modelo Usuario (nuestro perfil)
class UsuarioInline(admin.StackedInline):
    model = Usuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario (Rol)'
    fk_name = 'user_django'

# Define un nuevo UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_rol')

    def get_rol(self, instance):
        try:
            return instance.usuario.get_rol_display()
        except Usuario.DoesNotExist:
            return 'Sin Rol Asignado'
    get_rol.short_description = 'Rol'

# Vuelve a registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Para mejorar la visualización en el admin
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'estado_lead', 'fecha_ingreso', 'id_usuario_atencion')
    list_filter = ('estado_lead', 'fecha_ingreso', 'id_medio_contacto')
    search_fields = ('nombre_completo', 'telefono', 'email')

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'dni', 'email')
    search_fields = ('dni', 'email', 'id_lead__nombre_completo')

class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('id_matricula', 'id_cliente', 'id_programa', 'id_modalidad', 'estado', 'fecha_inscripcion')
    list_filter = ('estado', 'id_modalidad', 'id_programa')
    search_fields = ('id_cliente__id_lead__nombre_completo', 'id_cliente__dni')

class PagoAdmin(admin.ModelAdmin):
    list_display = ('id_pago', 'id_matricula', 'concepto', 'monto', 'fecha_pago')
    list_filter = ('concepto', 'fecha_pago', 'id_medio_pago')
    search_fields = ('id_matricula__id_cliente__id_lead__nombre_completo',)

# Registro de modelos
admin.site.register(Usuario)
admin.site.register(MedioContacto)
admin.site.register(Modalidad)
admin.site.register(MedioPago)
admin.site.register(ProgramaAcademico)
admin.site.register(Departamento)
admin.site.register(Provincia)
admin.site.register(Distrito)
admin.site.register(Lead, LeadAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(LeadInteresPrograma)
admin.site.register(Matricula, MatriculaAdmin)
admin.site.register(Pago, PagoAdmin)
