from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    # Ej: /gestion/
    path('', views.dashboard, name='dashboard'),
    # Ej: /gestion/leads/
    path('leads/', views.listar_leads, name='listar_leads'),
    # Ej: /gestion/leads/crear/
    path('leads/crear/', views.crear_lead, name='crear_lead'),
    # Ej: /gestion/leads/5/convertir/
    path('leads/<int:lead_id>/convertir/', views.convertir_lead_a_cliente, name='convertir_lead'),
    # URL para actualizar estado de lead vía AJAX
    path('leads/<int:lead_id>/actualizar-estado/', views.actualizar_estado_lead, name='actualizar_estado_lead'),
    # Ej: /gestion/matriculas/
    path('matriculas/', views.listar_matriculas, name='listar_matriculas'),
    # Ej: /gestion/matriculas/3/
    path('matriculas/<int:matricula_id>/', views.detalle_matricula, name='detalle_matricula'),
    # Ej: /gestion/clientes/1/editar/
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    # URL para poblar la BD con datos de ejemplo
    path('poblar-bd/', views.poblar_bd_ejemplo, name='poblar_bd'),
    path('consulta-sql/', views.consulta_sql, name='consulta_sql'),
    # API endpoint
    path('api/leads/crear/', views.api_crear_lead, name='api_crear_lead'),
] 