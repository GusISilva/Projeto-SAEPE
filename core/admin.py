# core/admin.py

from django.contrib import admin
from .models import Escola, Ocorrencia, Relatorio, Visita

admin.site.register(Escola)
admin.site.register(Ocorrencia)
admin.site.register(Relatorio)
admin.site.register(Visita)