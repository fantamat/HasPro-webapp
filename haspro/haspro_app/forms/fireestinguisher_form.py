from django import forms
from ..models import Firedistinguisher

from .utils import WidgetClassForm, DateInput


class FiredistinguisherForm(WidgetClassForm):
    class Meta:
        model = Firedistinguisher
        fields = ('kind', 'size', 'power', 'manufacturer', 'serial_number', 'eliminated', 'manufactured_year', 'next_inspection', 'next_periodic_test')
        widgets = {
            'kind': forms.Select(attrs={'class': 'form-control'}),
            'size': forms.NumberInput(attrs={'class': 'form-control'}),
            'power': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'eliminated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manufactured_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'next_inspection': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_periodic_test': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
