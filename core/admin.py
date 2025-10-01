# core/admin.py

from django.contrib import admin
from .models import Escola, Ocorrencia, Relatorio

admin.site.register(Escola)
admin.site.register(Ocorrencia)
admin.site.register(Relatorio)