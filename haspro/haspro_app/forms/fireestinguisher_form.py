from django import forms
from ..models import Firedistinguisher

from .utils import WidgetClassForm

class FiredistinguisherForm(WidgetClassForm):
    class Meta:
        model = Firedistinguisher
        fields = ('kind', 'type', 'manufacturer', 'serial_number', 'eliminated', 'last_inspection', 'manufactured_year', 'last_fullfilment')
        widgets = {
            'kind': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'eliminated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'last_inspection': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'manufactured_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'last_fullfilment': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
