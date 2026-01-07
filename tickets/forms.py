"""
Formularios para el sistema de tickets
"""
from django import forms
from .models import Ticket, Observacion


class TicketForm(forms.ModelForm):
    """Formulario para crear/editar tickets"""
    
    class Meta:
        model = Ticket
        fields = [
            'codigo', 'titulo', 'descripcion', 'prioridad',
            'estado', 'categoria', 'proveedor', 'elemento', 'dc',
            'fecha_inicio', 'fecha_cierre', 'usuario_asignado'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: STA-00507174'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Título del ticket'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Descripción detallada del incidente o requerimiento'
            }),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'elemento': forms.Select(attrs={'class': 'form-select'}),
            'dc': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'fecha_cierre': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'usuario_asignado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'dc': 'Data Center',
        }


class ObservacionForm(forms.ModelForm):
    """Formulario para agregar observaciones"""
    
    class Meta:
        model = Observacion
        fields = ['comentario', 'tipo']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Escriba su observación aquí...'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }
