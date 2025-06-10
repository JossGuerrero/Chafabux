from django import forms
from django.contrib.auth.models import User
from .models import Producto
from .models import Perfil

class PerfilFotoForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'cantidad', 'imagen']

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']