# core/forms.py
from django import forms
from .models import Escola # O modelo já existe em core/models.py

class EscolaSelectForm(forms.Form):
    escola = forms.ModelChoiceField(
        # Busca todas as escolas do banco de dados, ordenadas pelo nome
        queryset=Escola.objects.all().order_by('nome'), 
        empty_label="--- Todas as Escolas ---",
        label="Filtrar por Escola",
        required=False, # O filtro não é obrigatório
        # Aplica o estilo Bootstrap 5
        widget=forms.Select(attrs={'class': 'form-select'}) 
    )