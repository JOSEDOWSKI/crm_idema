from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    # Ruta raíz de la app, redirige al dashboard
    path('', views.superadmin_dashboard, name='dashboard'),
    
    # Rutas principales
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Rutas de Leads
    path('leads/', views.listar_leads, name='listar_leads'),
    path('leads/crear/', views.crear_lead, name='crear_lead'),
    path('leads/exportar/', views.exportar_leads_csv, name='exportar_leads_csv'),
    path('leads/<int:lead_id>/', views.detalle_lead, name='detalle_lead'),
    path('leads/<int:lead_id>/observaciones/exportar/', views.exportar_observaciones_csv, name='exportar_observaciones_csv'),
    path('leads/convertir/<int:lead_id>/', views.convertir_lead_a_cliente, name='convertir_lead'),
    # path('leads/actualizar_estado/<int:lead_id>/', views.actualizar_estado_lead, name='actualizar_estado_lead'),
    
    # Rutas de Matrículas y Clientes
    path('matriculas/', views.listar_matriculas, name='listar_matriculas'),
    path('matriculas/exportar/', views.exportar_matriculas_csv, name='exportar_matriculas_csv'),
    path('matriculas/<int:matricula_id>/', views.detalle_matricula, name='detalle_matricula'),
    path('matriculas/<int:matricula_id>/observaciones/exportar/', views.exportar_observaciones_matricula_csv, name='exportar_observaciones_matricula_csv'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    
    # Rutas Académicas (Notas y Asistencias)
    path('matriculas/<int:matricula_id>/notas/', views.gestionar_notas_matricula, name='gestionar_notas_matricula'),
    path('matriculas/<int:matricula_id>/asistencias/', views.gestionar_asistencias_matricula, name='gestionar_asistencias_matricula'),
    path('matriculas/<int:matricula_id>/notas/exportar/', views.exportar_notas_csv, name='exportar_notas_csv'),
    path('matriculas/<int:matricula_id>/asistencias/exportar/', views.exportar_asistencias_csv, name='exportar_asistencias_csv'),
    
    # Rutas de utilidades y API
    path('sql/', views.consulta_sql, name='consulta_sql'),
    path('tablas/', views.ver_todas_tablas, name='ver_todas_tablas'),
    path('super-dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('poblar-bd/', views.poblar_bd_ejemplo, name='poblar_bd'),
    # path('api/leads/crear/', views.api_crear_lead, name='api_crear_lead'),

    # Página de acceso denegado
    path('no-access/', views.no_access_view, name='no_access'),

    # Rutas de catálogos (solo superuser)
    path('catalogo/<str:modelo>/', views.catalogo_list, name='catalogo_list'),
    path('catalogo/<str:modelo>/crear/', views.catalogo_create, name='catalogo_create'),
    path('catalogo/<str:modelo>/editar/<int:pk>/', views.catalogo_edit, name='catalogo_edit'),
    path('catalogo/<str:modelo>/eliminar/<int:pk>/', views.catalogo_delete, name='catalogo_delete'),

    # Rutas de empleados
    path('empleados/', views.listar_empleados, name='listar_empleados'),
    path('empleados/nuevo/', views.crear_empleado, name='crear_empleado'),
    path('empleados/<int:empleado_id>/editar/', views.editar_empleado, name='editar_empleado'),
    path('empleados/<int:empleado_id>/eliminar/', views.eliminar_empleado, name='eliminar_empleado'),
    path('empleados/<int:empleado_id>/', views.detalle_empleado, name='detalle_empleado'),
    path('empleados/nuevo-con-acceso/', views.crear_empleado_con_acceso, name='crear_empleado_con_acceso'),

    # Rutas de documentos
    path('documentos/', views.listar_documentos, name='listar_documentos'),
    path('documentos/subir/', views.subir_documento, name='subir_documento'),
    path('documentos/<int:documento_id>/', views.detalle_documento, name='detalle_documento'),
    path('documentos/<int:documento_id>/resenar/', views.resenar_documento, name='resenar_documento'),
    path('panel-presencial/', views.panel_presencial, name='panel_presencial'),
    path('asistencia-grupal-presencial/', views.asistencia_grupal_presencial, name='asistencia_grupal_presencial'),
    path('menu-rol/', views.menu_rol, name='menu_rol'),
    path('panel-profesor/', views.panel_profesor, name='panel_profesor'),
    path('panel-estudiante/', views.panel_estudiante, name='panel_estudiante'),
    path('finanzas/', views.panel_gestion_finanzas, name='panel_gestion_finanzas'),
] 
urlpatterns += [
    path('programas-malla/', views.listar_programas_malla, name='listar_programas_malla'),
    path('programas-malla/<int:programa_id>/editar/', views.editar_malla_curricular, name='editar_malla_curricular'),
    path('roles/', views.gestionar_roles, name='gestionar_roles'),
    path('roles/crear/', views.crear_rol, name='crear_rol'),
    path('roles/<int:rol_id>/editar/', views.editar_rol, name='editar_rol'),
    path('roles/<int:rol_id>/eliminar/', views.eliminar_rol, name='eliminar_rol'),
] 