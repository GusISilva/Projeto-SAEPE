from django import forms
from .models import Visita, Escola, DadosFicticiosEscola, VisitaTecnica

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['escola', 'recebido_por', 'data_visita', 'hora_visita', 'objetivo', 'observacoes']
        widgets = {
            'escola': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'recebido_por': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de quem recebeu a visita', 'required': True}),
            'data_visita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'hora_visita': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Acompanhamento pedagógico, Inspeção de infraestrutura...'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Anote observações importantes sobre a visita...'}),
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
    escola = forms.ChoiceField(
        choices=[],
        required=False,
        label="Filtrar por Escola",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            lista_de_escolas = DadosFicticiosEscola.objects.values_list('escola', 'escola').distinct().order_by('escola')
            escolhas = [('', 'Todas as Escolas (Visão Geral)')] + list(lista_de_escolas)
        except Exception:
            escolhas = [('', 'Todas as Escolas (Visão Geral)')]
        self.fields['escola'].choices = escolhas


class VisitaTecnicaForm(forms.ModelForm):
    escola = forms.ChoiceField(label="Escola", choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    data_visita = forms.DateField(label="Data da Visita", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
    tecnico_gre = forms.ChoiceField(label="Técnico/Analista - GRE", choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    servidor_escola = forms.CharField(label="Servidor da Escola", widget=forms.TextInput(attrs={'class': 'form-control'}))
    demanda = forms.CharField(label="Demanda", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    encaminhamento = forms.CharField(label="Encaminhamento", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    observacao = forms.CharField(label="Observação", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)

    class Meta:
        model = VisitaTecnica
        fields = ['escola', 'data_visita', 'tecnico_gre', 'servidor_escola', 'demanda', 'encaminhamento', 'observacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            escolas = DadosFicticiosEscola.objects.values_list('escola', 'escola').distinct().order_by('escola')
            tecnicos = VisitaTecnica.objects.values_list('tecnico_gre', 'tecnico_gre').exclude(tecnico_gre=None).distinct().order_by('tecnico_gre')
            self.fields['escola'].choices = [('', 'Selecione a escola...')] + list(escolas)
            self.fields['tecnico_gre'].choices = [('', 'Selecione o técnico...')] + list(tecnicos)
        except Exception:
            # Caso o banco ainda não tenha tabelas (ex: antes das migrações)
            self.fields['escola'].choices = [('', 'Selecione a escola...')]
            self.fields['tecnico_gre'].choices = [('', 'Selecione o técnico...')]
