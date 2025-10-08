# core/forms.py

from django import forms
# Importa o modelo de Visita (assumindo que ele está em models.py) e o modelo Escola
from .models import Visita, Escola 

# ----------------------------------------------------
# 1. VISITA FORM (Seu formulário de registro original)
# ----------------------------------------------------
class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['escola', 'recebido_por', 'data_visita', 'hora_visita', 'objetivo', 'observacoes']
        # ... (restante do seu código VisitaForm) ...
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

# ----------------------------------------------------
# 2. ESCOLA SELECT FORM (O NOVO formulário de filtro)
# ----------------------------------------------------
class EscolaSelectForm(forms.Form):
    escola = forms.ModelChoiceField(
        queryset=Escola.objects.all().order_by('nome'), 
        empty_label="--- Todas as Escolas ---",
        label="Filtrar por Escola",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}) 
    )