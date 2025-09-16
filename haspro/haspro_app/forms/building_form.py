from django import forms
from ..models import Building

from .utils import WidgetClassForm

class BuildingForm(WidgetClassForm):
    class Meta:
        model = Building
        fields = ('building_id', 'address', 'city', 'zipcode', 'note', 'company', 'owner', 'manager')
        widgets = {
            'building_id': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
        }
