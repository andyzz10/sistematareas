from django import forms
from .models import Task
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe un título'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe una descripción'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input text-center'}),
        }
class RegistroJugadorForm(UserCreationForm):
    # Agregamos oninput para que si el usuario teclea una letra, se borre inmediatamente
    cedula = forms.CharField(
        max_length=10, 
        required=True, 
        label="Cédula de Identidad",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ej: 1308090700',
            'pattern': '[0-9]+',
            'title': 'Solo se permiten números',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '')" # Magia de Frontend
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields