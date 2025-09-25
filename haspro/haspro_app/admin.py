from django.contrib import admin
from .models import (
    Company, 
    BuildingOwner, 
    BuildingManager, 
    Building, 
    Fault, 
    Firedistinguisher, 
    FiredistinguisherPlacement,
    FiredistinguisherServiceAction,
    InspectionRecord,
    FaultInspection,
    FaultPhoto
)


REGISTERED_MODELS = [
    Company, 
    BuildingOwner, 
    BuildingManager, 
    Building, 
    Fault, 
    Firedistinguisher, 
    FiredistinguisherPlacement,
    FiredistinguisherServiceAction,
    InspectionRecord,
    FaultInspection,
    FaultPhoto
]

SKIP_FIELDS = {
}


for model in REGISTERED_MODELS:
    admin_class = type(
        f"{model.__name__}Admin",
        (admin.ModelAdmin,),
        {"list_display": [field.name for field in model._meta.fields if field.name not in SKIP_FIELDS]}
    )
    admin.site.register(model, admin_class)

