# core/forms.py

from django import forms
from .models import Visita, Escola

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['escola', 'recebido_por', 'data_visita', 'hora_visita', 'objetivo', 'observacoes']
        widgets = {
            'escola': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'recebido_por': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de quem recebeu a visita',
                'required': True
            }),
            'data_visita': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'hora_visita': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'objetivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Acompanhamento pedagógico, Inspeção de infraestrutura...'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Anote observações importantes sobre a visita...'
            }),
        }
        labels = {
            'escola': 'Escola Visitada',
            'recebido_por': 'Recebido por',
            'data_visita': 'Data da Visita',
            'hora_visita': 'Horário',
            'objetivo': 'Objetivo da Visita',
            'observacoes': 'Observações'
        }