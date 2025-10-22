# core/views.py

import pandas as pd
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import pandas as pd
from django.shortcuts import render, redirect # Importação de render e redirect (agora consolidada)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Escola, Ocorrencia, Relatorio, Visita, DadosFicticiosEscola# V2: Importe os dois formulários necessários
from .forms import VisitaForm, EscolaSelectForm 


#registro de novos usuários
def registro_view(request):
    if request.user.is_authenticated:
        return redirect('main_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'registro.html')
        
        if len(password) < 8:
            messages.error(request, 'A senha deve ter no mínimo 8 caracteres.')
            return render(request, 'registro.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Conta criada com sucesso! Bem-vindo!')
        return redirect('main_dashboard')
    
    return render(request, 'registro.html')

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

@login_required(login_url='login')
def main_dashboard_view(request):
    return render(request, 'main_dashboard.html')

@login_required(login_url='login')
def relatorios_view(request):
    if request.method == 'POST':
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
        return redirect('main_dashboard')
    else:
        todas_escolas = Escola.objects.all()
        todas_ocorrencias = Ocorrencia.objects.all()
        context = {
            'escolas': todas_escolas,
            'ocorrencias': todas_ocorrencias,
        }
        return render(request, 'relatorios.html', context)

@login_required(login_url='login')
def visitas_view(request):
    if request.method == 'POST':
        tipo_registro = request.POST.get('tipo_registro', 'realizada')
        form = VisitaForm(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.visitante = request.user
            visita.status = tipo_registro
            if tipo_registro == 'agendada':
                visita.recebido_por = ''
            visita.save()
            
            if tipo_registro == 'agendada':
                messages.success(request, 'Visita agendada com sucesso!')
            else:
                messages.success(request, 'Visita registrada com sucesso!')
            return redirect('visitas')
        else:
            messages.error(request, 'Erro ao registrar. Verifique os dados.')
    else:
        form = VisitaForm()
    
    visitas_realizadas = Visita.objects.filter(
        visitante=request.user, 
        status='realizada'
    ).select_related('escola')
    
    visitas_agendadas = Visita.objects.filter(
        visitante=request.user,
        status='agendada'
    ).select_related('escola')
    
    context = {
        'form': form,
        'visitas_realizadas': visitas_realizadas,
        'visitas_agendadas': visitas_agendadas,
    }
    
    return render(request, 'visitas.html', context)


@login_required(login_url='login')
def analise_dashboard_view(request):
    
    form = EscolaSelectForm(request.GET)
    escola_nome_filtro = None
    titulo_sufixo = " - Visão Geral"
    
    if form.is_valid():
        escola_nome_filtro = form.cleaned_data.get('escola')
        
        if escola_nome_filtro:
            titulo_sufixo = f" - {escola_nome_filtro}"
        else:
            escola_nome_filtro = None 
            titulo_sufixo = " - Visão Geral"
            
    erro = None
    
    try:
        base_query = DadosFicticiosEscola.objects.all()

        if escola_nome_filtro:
            base_query = base_query.filter(escola=escola_nome_filtro)

        dados_para_grafico = base_query.values(
            'escola', 
            'proficiencia_mt_2023' 
        ).order_by('-proficiencia_mt_2023') 
        
        dados_grafico_json = json.dumps(list(dados_para_grafico))

        df_tabela_1 = pd.DataFrame(list(
            base_query.values('escola', 'saepe_2022', 'saepe_2023')
        ))
        df_tabela_1.columns = ['Escola', 'SAEPE 2022', 'SAEPE 2023']
        tabela_1_html = df_tabela_1.to_html(classes='table table-striped', index=False)
        
        df_tabela_2 = pd.DataFrame(list(
            base_query.values('escola', 'proficiencia_lp_2023', 'proficiencia_mt_2023')
        ))
        df_tabela_2.columns = ['Escola', 'Proficiência LP 2023', 'Proficiência MT 2023']
        tabela_2_html = df_tabela_2.to_html(classes='table table-striped', index=False)

    except Exception as e:
        erro = f"Ocorreu um erro ao consultar os dados: {e}"
        dados_grafico_json = '[]'
        tabela_1_html = "<p>Não foi possível carregar os dados.</p>"
        tabela_2_html = "<p>Não foi possível carregar os dados.</p>"


    context = {
        'form': form, 
        'titulo_sufixo': titulo_sufixo,
        'erro': erro,
        
        'dados_grafico_json': dados_grafico_json,
        
        'analise_escola': tabela_1_html,
        'media_ideb': tabela_2_html, 
    }
    
    return render(request, 'analise_dashboard.html', context)