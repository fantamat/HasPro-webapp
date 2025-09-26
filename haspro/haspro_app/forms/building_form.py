from django import forms
from ..models import Building

from .utils import WidgetClassForm, DateInput

class BuildingForm(WidgetClassForm):
    class Meta:
        model = Building
        fields = ('building_id', 'address', 'city', 'zipcode', 'note', 'company', 'owner', 'manager', 'last_inspection_date', 'inspection_interval_days')
        widgets = {
            'building_id': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'last_inspection_date': DateInput(attrs={'class': 'form-control'}),
            'inspection_interval_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }
