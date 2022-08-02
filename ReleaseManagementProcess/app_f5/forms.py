from tkinter import Widget
from django import forms
from app_f5.models import F5Pools

class PoolForm(forms.ModelForm):
    class Meta:
        model = F5Pools
        fields = '__all__'
        #fields = ['name']
        widgets = {
            "name": forms.TextInput(attrs={'class':'form-control','placeholder':'new pool name'}),
            "project": forms.TextInput(attrs={'class':'form-control','placeholder':'project name'}),
            "server": forms.TextInput(attrs={'class':'form-control','placeholder':'server name'}),
            "environment": forms.Select(attrs={'class':'form-select','placeholder':'environment'}),
        }
        required=True

        #def __init__(self, *args, **kwargs):
        #    super().__init__(*args, **kwargs)
        #    for name, field in self.fieldls.itmes():
        #        field.widget.attrs = {'class':'form-control'}
