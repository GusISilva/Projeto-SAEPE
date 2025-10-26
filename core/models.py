# core/models.py

from django.db import models
from django.contrib.auth.models import User

# Modelo para representar cada escola
class Escola(models.Model):
    nome = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

# Modelo para as possíveis ocorrências que podem ser marcadas
class Ocorrencia(models.Model):
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.descricao

# Modelo para o relatório preenchido pelo visitante
class Relatorio(models.Model):
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE)
    visitante = models.ForeignKey(User, on_delete=models.CASCADE)
    ocorrencias = models.ManyToManyField(Ocorrencia)
    detalhes = models.TextField(blank=True, null=True, verbose_name="Detalhes da visita")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Relatório para {self.escola.nome} em {self.data_criacao.strftime('%d/%m/%Y')}"

class Visita(models.Model):
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('realizada', 'Realizada'),
    ]
    
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name='visitas')
    visitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visitas_realizadas')
    recebido_por = models.CharField(max_length=200, verbose_name="Recebido por", blank=True)
    data_visita = models.DateField(verbose_name="Data da visita")
    hora_visita = models.TimeField(verbose_name="Horário da visita", null=True, blank=True)
    objetivo = models.CharField(max_length=300, verbose_name="Objetivo da visita", blank=True)
    observacoes = models.TextField(verbose_name="Observações", blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='realizada')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_visita', '-hora_visita']
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"

    def __str__(self):
        return f"Visita à {self.escola.nome} em {self.data_visita.strftime('%d/%m/%Y')} - {self.get_status_display()}"
    
class DadosFicticiosEscola(models.Model):
    escola = models.CharField(max_length=255)
    modalidade = models.CharField(max_length=100)
    alunos_previstos_2023 = models.IntegerField(null=True, blank=True)
    percentual_peso = models.FloatField(null=True, blank=True)
    saepe_2022 = models.FloatField(null=True, blank=True)
    saepe_2023 = models.FloatField(null=True, blank=True)
    proficiencia_lp_2023 = models.FloatField(null=True, blank=True)
    proficiencia_mt_2023 = models.FloatField(null=True, blank=True)
    matricula_efaf_2024 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.escola


# NOSSO NOVO MODELO PARA AS VISITAS TÉCNICAS
class VisitaTecnica(models.Model):
    # Usamos os nomes da sua planilha, mas em formato Python
    # (minúsculas, sem espaços, sem acentos)
    
    escola = models.CharField(max_length=255)
    data_visita = models.DateField(null=True, blank=True) # Melhor tipo para datas
    tecnico_gre = models.CharField(max_length=255, null=True, blank=True)
    servidor_escola = models.CharField(max_length=255, null=True, blank=True)
    demanda = models.TextField(null=True, blank=True) # TextField é melhor para textos longos
    encaminhamento = models.TextField(null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        # Isto é o que vai aparecer no painel de admin do Django
        return f"Visita em {self.escola} ({self.data_visita})"