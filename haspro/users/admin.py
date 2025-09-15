from django.contrib import admin
from .models import (
    User,
    Project,
    ProjectPermissions
)
# Register your models here.
# admin.site.register(File)


REGISTERED_MODELS = [
    User,
    Project,
    ProjectPermissions
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

