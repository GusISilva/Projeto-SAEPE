# core/views.py

import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Escola, Ocorrencia, Relatorio

# --- Views de Autenticação ---

# NOVA VIEW: Para registro de novos usuários
def registro_view(request):
    if request.user.is_authenticated:
        return redirect('main_dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Loga o usuário automaticamente após o registro
            return redirect('main_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registro.html', {'form': form})

# VIEW MODIFICADA: Redireciona para o novo dashboard principal
def login_view(request):
    if request.user.is_authenticated:
        return redirect('main_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


# --- Views da Aplicação (Protegidas por Login) ---

# NOVA VIEW: O Dashboard Principal
@login_required(login_url='login')
def main_dashboard_view(request):
    # Esta view por enquanto apenas renderiza a página de boas-vindas.
    # No futuro, você pode adicionar dados resumidos aqui.
    return render(request, 'main_dashboard.html')

# VIEW RENOMEADA: O antigo dashboard agora é o dashboard de análise
@login_required(login_url='login')
def analise_dashboard_view(request):
    context = {}
    try:
        df = pd.read_excel('dados_escolas.xlsx')
        # ... (toda a sua lógica Pandas continua aqui)
        analise_escola = df['Escola'].value_counts().to_frame().to_html(classes='table table-striped')
        media_ideb = df.groupby('Escola')['IDEB'].mean().to_frame().to_html(classes='table table-striped')
        context = {
            'analise_escola': analise_escola,
            'media_ideb': media_ideb,
        }
    except Exception as e:
        context['erro'] = f"Ocorreu um erro: {e}"
        
    return render(request, 'analise_dashboard.html', context)


# VIEW EXISTENTE: Sem grandes alterações necessárias
@login_required(login_url='login')
def relatorios_view(request):
    if request.method == 'POST':
        # ... (lógica do POST continua a mesma)
        escola_id = request.POST.get('escola')
        ocorrencias_ids = request.POST.getlist('ocorrencias')
        detalhes_texto = request.POST.get('detalhes')
        escola_obj = Escola.objects.get(id=escola_id)
        novo_relatorio = Relatorio.objects.create(
            escola=escola_obj,
            visitante=request.user,
            detalhes=detalhes_texto
        )
        novo_relatorio.ocorrencias.set(ocorrencias_ids)
        return redirect('main_dashboard') # Redireciona para o dashboard principal
    else:
        todas_escolas = Escola.objects.all()
        todas_ocorrencias = Ocorrencia.objects.all()
        context = {
            'escolas': todas_escolas,
            'ocorrencias': todas_ocorrencias,
        }
        return render(request, 'relatorios.html', context)