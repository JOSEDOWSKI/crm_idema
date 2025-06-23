from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    # Ruta raíz de la app, redirige al dashboard
    path('', views.dashboard, name='dashboard'), 
    
    # Rutas principales
    path('dashboard/', views.dashboard, name='dashboard_explicit'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Rutas de Leads
    path('leads/', views.listar_leads, name='listar_leads'),
    path('leads/crear/', views.crear_lead, name='crear_lead'),
    path('leads/<int:lead_id>/', views.detalle_lead, name='detalle_lead'),
    path('leads/convertir/<int:lead_id>/', views.convertir_lead_a_cliente, name='convertir_lead'),
    path('leads/actualizar_estado/<int:lead_id>/', views.actualizar_estado_lead, name='actualizar_estado_lead'),
    
    # Rutas de Matrículas y Clientes
    path('matriculas/', views.listar_matriculas, name='listar_matriculas'),
    path('matriculas/<int:matricula_id>/', views.detalle_matricula, name='detalle_matricula'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    
    # Rutas de utilidades y API
    path('sql/', views.consulta_sql, name='consulta_sql'),
    path('poblar-bd/', views.poblar_bd_ejemplo, name='poblar_bd'),
    path('api/leads/crear/', views.api_crear_lead, name='api_crear_lead'),
] 