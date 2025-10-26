# core/forms.py

from django import forms
from .models import Visita, Escola, DadosFicticiosEscola, VisitaTecnica

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

# ----------------------------------------------------
# 3. FORMULÁRIO PARA O POPUP DE VISITA TÉCNICA (NOVO)
# ----------------------------------------------------
class VisitaTecnicaForm(forms.ModelForm):

    # 1. Vamos criar uma lista de ESCOLAS para o dropdown
    # Buscamos do seu banco de dados de escolas (o do dashboard)
    lista_escolas = list(
        DadosFicticiosEscola.objects.values_list('escola', 'escola')
                                   .distinct()
                                   .order_by('escola')
    )
    ESCOLAS_CHOICES = [('', 'Selecione a escola...')] + lista_escolas

    # 2. Vamos criar uma lista de TÉCNICOS para o dropdown
    # Buscamos da própria tabela de visitas que acabámos de importar
    lista_tecnicos = list(
        VisitaTecnica.objects.values_list('tecnico_gre', 'tecnico_gre')
                             .exclude(tecnico_gre=None) # Remove valores nulos
                             .distinct()
                             .order_by('tecnico_gre')
    )
    TECNICOS_CHOICES = [('', 'Selecione o técnico...')] + lista_tecnicos

    # 3. Definimos os campos do formulário
    escola = forms.ChoiceField(
        label="Escola",
        choices=ESCOLAS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_visita = forms.DateField(
        label="Data da Visita",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False # <--- ADICIONE ESTA LINHA
    )
    tecnico_gre = forms.ChoiceField(
        label="Técnico/Analista - GRE",
        choices=TECNICOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    servidor_escola = forms.CharField(
        label="Servidor da Escola",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    demanda = forms.CharField(
        label="Demanda",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    encaminhamento = forms.CharField(
        label="Encaminhamento",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False # Este campo é opcional
    )
    observacao = forms.CharField(
        label="Observação",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False # Este campo é opcional
    )

    class Meta:
        model = VisitaTecnica  # O nosso "molde"
        # Os campos do modelo que este formulário vai usar
        fields = ['escola', 'data_visita', 'tecnico_gre', 'servidor_escola', 
                  'demanda', 'encaminhamento', 'observacao']