
from django.urls import path, re_path


app_name = 'haspro_app'

from . import views

urlpatterns = [
	path('owners/', views.buildingowner_list, name='buildingowner-list'),
    path('owners/create/', views.buildingowner_create, name='buildingowner-create'),
	path('owners/<int:pk>/edit/', views.buildingowner_edit, name='buildingowner-edit'),
	path('owners/<int:pk>/delete/', views.buildingowner_delete, name='buildingowner-delete'),
    
	path('buildings/', views.building_list, name='building-list'),
    path('buildings/create/', views.building_create, name='building-create'),
    path('buildings/<int:pk>/edit/', views.building_edit, name='building-edit'),
	path('buildings/<int:pk>/delete/', views.building_delete, name='building-delete'),
    
	path('firedistinguisher/', views.firedistinguisher_list, name='firedistinguisher-list'),
	path('firedistinguisher/create/', views.firedistinguisher_create, name='firedistinguisher-create'),
    path('firedistinguisher/<int:pk>/edit/', views.firedistinguisher_edit, name='firedistinguisher-edit'),
    path('firedistinguisher/<int:pk>/delete/', views.firedistinguisher_delete, name='firedistinguisher-delete'),

	path('tools/', views.tools_view, name='tools-view'),

	path('import/building_manager/', views.import_building_manager_list, name='import-building-manager-list'),
	path('import/firedistinguisher/', views.import_firedistinguisher_list, name='import-firedistinguisher-list'),
    
    path('db/dump/snapshot/', views.get_db_snapshot, name='export-db-dump')
]
