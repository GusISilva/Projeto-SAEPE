# core/views.py

import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm # UserCreationForm não estava a ser usado
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html

from .models import Escola, Ocorrencia, Relatorio, Visita, DadosFicticiosEscola, VisitaTecnica
from .forms import VisitaForm, EscolaSelectForm, VisitaTecnicaForm

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
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Bem-vindo!')
            return redirect('main_dashboard')
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {e}')
            return render(request, 'registro.html')

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
                # Redireciona para o dashboard principal após o login
                return redirect('main_dashboard') 
            else:
                 messages.error(request, 'Nome de utilizador ou palavra-passe inválidos.')
        else:
             messages.error(request, 'Nome de utilizador ou palavra-passe inválidos.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Sessão terminada com sucesso.')
    return redirect('login')


@login_required(login_url='login')
def main_dashboard_view(request):
    return render(request, 'main_dashboard.html')

@login_required(login_url='login')
def relatorios_view(request):
    if request.method == 'POST':
        return redirect('main_dashboard')
    else:
        return render(request, 'relatorios.html', context)


@login_required(login_url='login')
def visitas_view(request):
    
    if request.method == 'POST':
        form = VisitaTecnicaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Visita registada com sucesso!')
                return redirect('visitas') # Volta para a mesma página
            except Exception as e:
                 messages.error(request, f'Erro inesperado ao guardar a visita: {e}')
        else:
            error_message = 'Erro ao guardar. Por favor, verifique os dados: '
            for field, errors in form.errors.items():
                error_message += f"{field}: {', '.join(errors)} "
            messages.error(request, error_message)
           
    
    todas_visitas = VisitaTecnica.objects.all().order_by('-data_visita') 
    
    form_modal = VisitaTecnicaForm() 
    
    context = {
        'form_modal': form_modal,       
        'visitas': todas_visitas,      
    }
    
    return render(request, 'visitas.html', context) # Renderiza o seu template original



@login_required(login_url='login')
def analise_dashboard_view(request):
    
    form = EscolaSelectForm(request.GET or None) # Usar request.GET or None é mais seguro
    escola_nome_filtro = None
    titulo_sufixo = " - Visão Geral"
    
    if form.is_valid():
        escola_nome_filtro = form.cleaned_data.get('escola')
        if escola_nome_filtro:
            titulo_sufixo = f" - {escola_nome_filtro}"
        else:
            escola_nome_filtro = None # Garante que None é usado se 'Todas' for selecionado
            titulo_sufixo = " - Visão Geral"
            
    erro = None
    dados_grafico_json = '[]'
    tabela_1_html = "<p>Nenhum dado encontrado.</p>" # Mensagem padrão
    tabela_2_html = "<p>Nenhum dado encontrado.</p>" # Mensagem padrão
    
    try:
        base_query = DadosFicticiosEscola.objects.all()

        if escola_nome_filtro:
            base_query = base_query.filter(escola=escola_nome_filtro)

        dados_para_grafico = base_query.values(
            'escola', 
            'proficiencia_mt_2023' 
        ).order_by('-proficiencia_mt_2023') 
        
        dados_grafico_json = json.dumps(list(dados_para_grafico))

        dados_tabelas = list(base_query.values(
            'escola', 'saepe_2022', 'saepe_2023', 
            'proficiencia_lp_2023', 'proficiencia_mt_2023'
        ))

        if dados_tabelas: 
            for item in dados_tabelas:
                try:
                    url_perfil = reverse('perfil_escola', args=[item['escola']])
                    item['escola_link'] = format_html('<a href="{}">{}</a>', url_perfil, item['escola'])
                except Exception as link_error:
                    
                    item['escola_link'] = item['escola'] 
                    print(f"Erro ao gerar link para {item['escola']}: {link_error}") # Log para debug

            df_tabelas = pd.DataFrame(dados_tabelas)

            tabela_1_html = df_tabelas[['escola_link', 'saepe_2022', 'saepe_2023']].rename(
                columns={'escola_link': 'Escola', 'saepe_2022': 'SAEPE 2022', 'saepe_2023': 'SAEPE 2023'}
            ).to_html(classes='table table-striped table-hover', index=False, escape=False)
            
            tabela_2_html = df_tabelas[['escola_link', 'proficiencia_lp_2023', 'proficiencia_mt_2023']].rename(
                columns={'escola_link': 'Escola', 'proficiencia_lp_2023': 'Proficiência LP 2023', 'proficiencia_mt_2023': 'Proficiência MT 2023'}
            ).to_html(classes='table table-striped table-hover', index=False, escape=False)

    except Exception as e:
        erro = f"Ocorreu um erro ao consultar os dados: {e}"
        dados_grafico_json = '[]'
        tabela_1_html = f"<p>Erro ao carregar dados: {e}</p>"
        tabela_2_html = f"<p>Erro ao carregar dados: {e}</p>"

    context = {
        'form': form, 
        'titulo_sufixo': titulo_sufixo,
        'erro': erro,
        'dados_grafico_json': dados_grafico_json,
        'analise_escola': tabela_1_html, 
        'media_ideb': tabela_2_html,    #2
    }
    
    return render(request, 'analise_dashboard.html', context)


@login_required(login_url='login')
def perfil_escola_view(request, escola_nome):
    try:
        escola_nome_tratado = escola_nome.strip() 
        
        escola_info = get_object_or_404(DadosFicticiosEscola, escola=escola_nome_tratado)
        
        visitas_historico = VisitaTecnica.objects.filter(
            escola=escola_nome_tratado
        ).order_by('-data_visita') 

        context = {
            'escola_info': escola_info,
            'visitas_historico': visitas_historico,
        }
        
        return render(request, 'perfil_escola.html', context)

    except DadosFicticiosEscola.DoesNotExist:
         messages.error(request, f"Escola '{escola_nome}' não encontrada nos dados fictícios.")
         return redirect('analise_dashboard') 
    except Exception as e:
         messages.error(request, f"Ocorreu um erro ao carregar o perfil da escola: {e}")
         return redirect('analise_dashboard')