
from django.urls import path, re_path


app_name = 'haspro_app'

from . import views

urlpatterns = [
    path('', views.home, name='home'),

	path('owners/', views.buildingowner_list, name='buildingowner-list'),
    path('owners/create/', views.buildingowner_create, name='buildingowner-create'),
	path('owners/<int:pk>/edit/', views.buildingowner_edit, name='buildingowner-edit'),
	path('owners/<int:pk>/delete/', views.buildingowner_delete, name='buildingowner-delete'),
    
	path('managers/', views.buildingmanager_list, name='buildingmanager-list'),
    path('managers/create/', views.buildingmanager_create, name='buildingmanager-create'),
	path('managers/<int:pk>/edit/', views.buildingmanager_edit, name='buildingmanager-edit'),
	path('managers/<int:pk>/delete/', views.buildingmanager_delete, name='buildingmanager-delete'),
    
	path('buildings/', views.building_list, name='building-list'),
    path('buildings/create/', views.building_create, name='building-create'),
    path('buildings/<int:pk>/edit/', views.building_edit, name='building-edit'),
	path('buildings/<int:pk>/delete/', views.building_delete, name='building-delete'),
	path('buildings/<int:pk>/add-possible-fault/', views.add_possible_fault, name='add-possible-fault'),
    
	path('firedistinguisher/', views.firedistinguisher_list, name='firedistinguisher-list'),
	path('firedistinguisher/create/', views.firedistinguisher_create, name='firedistinguisher-create'),
    path('firedistinguisher/<int:pk>/edit/', views.firedistinguisher_edit, name='firedistinguisher-edit'),
    path('firedistinguisher/<int:pk>/delete/', views.firedistinguisher_delete, name='firedistinguisher-delete'),

	path('tools/', views.tools_view, name='tools-view'),

	path('import/building_manager/', views.import_building_manager_list, name='import-building-manager-list'),
	path('import/firedistinguisher/', views.import_firedistinguisher_list, name='import-firedistinguisher-list'),

    path('db/dump/snapshot/', views.get_db_snapshot, name='export-db-dump'),
    path('db/inspection/upload/', views.upload_inspection_records, name='upload-inspection-records'),
]
