from django import forms
from ..models import FiredistinguisherPlacement

from .utils import WidgetClassForm

class FiredistinguisherPlacementForm(WidgetClassForm):
    class Meta:
        model = FiredistinguisherPlacement
        fields = ('description', 'firedistinguisher', 'building')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'firedistinguisher': forms.Select(attrs={'class': 'form-select'}),
            'building': forms.Select(attrs={'class': 'form-select'}),
        }
