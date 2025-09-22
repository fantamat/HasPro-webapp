from django import forms
from ..models import BuildingManager


class BuildingManagerForm(forms.ModelForm):
    class Meta:
        model = BuildingManager
        fields = ['name', 'address', 'phone', 'phone2', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter manager name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'phone2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter second phone number (optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
        }
