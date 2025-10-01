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