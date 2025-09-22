from django import forms
from ..models import Firedistinguisher

from .utils import WidgetClassForm

class FiredistinguisherForm(WidgetClassForm):
    class Meta:
        model = Firedistinguisher
        fields = ('kind', 'type', 'manufacturer', 'serial_number', 'eliminated', 'manufactured_year', 'next_inspection')
        widgets = {
            'kind': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'eliminated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manufactured_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'next_inspection': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
