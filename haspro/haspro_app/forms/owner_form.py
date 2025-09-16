from django import forms
from ..models import BuildingOwner

from .utils import WidgetClassForm


class BuildingOwnerForm(WidgetClassForm):
    class Meta:
        model = BuildingOwner
        fields = ('name', 'address', 'city', 'zipcode', 'ico', 'dic')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control'}),
            'ico': forms.TextInput(attrs={'class': 'form-control'}),
            'dic': forms.TextInput(attrs={'class': 'form-control'}),
        }
