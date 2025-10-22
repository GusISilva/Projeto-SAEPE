# core/forms.py

from django import forms
# IMPORTANTE: Importamos os DOIS modelos de escola
from .models import Visita, Escola, DadosFicticiosEscola 

# ----------------------------------------------------
# 1. VISITA FORM (DEIXAMOS INTACTO, pois ele usa o model 'Escola' antigo)
# ----------------------------------------------------
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

# ----------------------------------------------------
# 2. ESCOLA SELECT FORM (CORRIGIDO para usar os dados da planilha)
# ----------------------------------------------------
class EscolaSelectForm(forms.Form):
    
    # 1. Busca os nomes das escolas no NOVO banco de dados (DadosFicticiosEscola)
    lista_de_escolas = list(
        DadosFicticiosEscola.objects.values_list('escola', 'escola') # (valor, texto_exibido)
                                   .distinct()                 # Garante que cada escola apareça só 1 vez
                                   .order_by('escola')         # Ordem alfabética
    )
    
    # 2. Adiciona a opção "Todas as Escolas" no começo
    ESCOLAS_CHOICES = [
        ('', 'Todas as Escolas (Visão Geral)') # O valor '' significa "nenhum filtro"
    ] + lista_de_escolas

    # 3. Cria o campo do formulário
    escola = forms.ChoiceField(
        choices=ESCOLAS_CHOICES, # Usa nossa lista dinâmica
        required=False,
        label="Filtrar por Escola",
        # Isso adiciona a classe CSS do Bootstrap para ficar bonito
        widget=forms.Select(attrs={'class': 'form-select'}) 
    )