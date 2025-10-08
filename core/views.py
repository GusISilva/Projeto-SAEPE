# core/views.py

import pandas as pd
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
from .models import Escola, Ocorrencia, Relatorio, Visita
# V2: Importe os dois formulários necessários
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
def analise_dashboard_view(request):
    context = {}
    try:
        df = pd.read_excel('dados_escolas.xlsx')
        analise_escola = df['Escola'].value_counts().to_frame().to_html(classes='table table-striped')
        media_ideb = df.groupby('Escola')['IDEB'].mean().to_frame().to_html(classes='table table-striped')
        context = {
            'analise_escola': analise_escola,
            'media_ideb': media_ideb,
        }
    except Exception as e:
        context['erro'] = f"Ocorreu um erro: {e}"

    return render(request, 'analise_dashboard.html', context)

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

# NOVA VIEW: Gerenciar Visitas
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

# VIEW RENOMEADA: O antigo dashboard agora é o dashboard de análise
@login_required(login_url='login')
def analise_dashboard_view(request):
    
    form = EscolaSelectForm(request.GET)
    escola_nome_filtro = None
    titulo_sufixo = " - Visão Geral"
    
    if form.is_valid():
        escola_obj = form.cleaned_data.get('escola')
        if escola_obj:
            escola_nome_filtro = escola_obj.nome 
            titulo_sufixo = f" - {escola_obj.nome}"
            
    # Valores padrões para evitar erro de variável não definida
    analise_escola = "Dados de registros não disponíveis."
    media_ideb = "Dados de IDEB não disponíveis."
    erro = None
    
    # ----------------------------------------------------
    # BLOCO TRY/EXCEPT PARA LIDAR COM O ARQUIVO FALTANTE
    # ----------------------------------------------------
    try:
        # Tenta ler o arquivo (Ajuste o caminho se necessário!)
        df = pd.read_excel('dados_escolas.xlsx')
        
        # 1. Aplicar a Filtragem no DataFrame
        if escola_nome_filtro:
            df_filtrado = df[df['Escola'] == escola_nome_filtro]
        else:
            df_filtrado = df

        # 2. Gerar as Análises com o DataFrame Filtrado
        
        # Lógica de Registros
        if escola_nome_filtro:
             # Exibe a contagem total de registros para a escola
             contagem_registros = pd.Series({'Total de Registros': len(df_filtrado)}).to_frame().to_html(classes='table table-striped')
        else:
             # Visão Geral: Contagem por todas as escolas
             contagem_registros = df_filtrado['Escola'].value_counts().to_frame().to_html(classes='table table-striped')

        # Lógica de Média IDEB
        media_ideb_data = df_filtrado.groupby('Escola')['IDEB'].mean().to_frame().to_html(classes='table table-striped', header=['Média do IDEB'])

        # Atualiza as variáveis de contexto se o arquivo foi lido com sucesso
        analise_escola = contagem_registros
        media_ideb = media_ideb_data
        
    except FileNotFoundError:
        # Se o arquivo não existir, exibe uma mensagem de erro na tela
        erro = "Arquivo de dados 'dados_escolas.xlsx' não encontrado. Gráficos de análise não puderam ser gerados."
        
    except Exception as e:
        # Lida com outros erros (ex: Pandas não conseguiu processar o XLSX)
        erro = f"Ocorreu um erro ao processar os dados: {e}"

    # Monta o contexto final
    context = {
        'form': form, 
        'analise_escola': analise_escola,
        'media_ideb': media_ideb,
        'titulo_sufixo': titulo_sufixo,
        'erro': erro,
    }
    
    return render(request, 'analise_dashboard.html', context)