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