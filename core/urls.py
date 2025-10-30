# Em SAEPE/urls.py

from django.contrib import admin
from django.urls import path
from core import views 



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Suas URLs ---
    path('', views.main_dashboard_view, name='main_dashboard'), 
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('relatorios/', views.relatorios_view, name='relatorios'),
    path('dashboard-analise/', views.analise_dashboard_view, name='analise_dashboard'),
    path('visitas/', views.visitas_view, name='visitas'), 
        path('escola/<str:escola_nome>/', views.perfil_escola_view, name='perfil_escola'),
]