# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URLs de Autenticação
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # URLs Principais da Aplicação
    path('', views.main_dashboard_view, name='main_dashboard'),
    path('dashboard-analise/', views.analise_dashboard_view, name='analise_dashboard'),
    path('relatorios/', views.relatorios_view, name='relatorios'),
    path('visitas/', views.visitas_view, name='visitas'), 
]