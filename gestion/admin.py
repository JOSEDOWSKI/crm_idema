from django.contrib import admin
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
