import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Escola, Ocorrencia, Relatorio
from .forms import EscolaSelectForm # <-- NOVA IMPORTAÇÃO


#registro de novos usuários
def registro_view(request):
    if request.user.is_authenticated:
        return redirect('main_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validações 
      
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'registro.html')
        
        if len(password) < 8:
            messages.error(request, 'A senha deve ter no mínimo 8 caracteres.')
            return render(request, 'registro.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        
        
        # Mensagem de sucesso
        messages.success(request, 'Conta criada com sucesso! Bem-vindo!')
        
        # Redireciona para o dashboard principal
        return redirect('main_dashboard')
    
    return render(request, 'registro.html')

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
    
    # VIEW RENOMEADA: O antigo dashboard agora é o dashboard de análise
@login_required(login_url='login')
def analise_dashboard_view(request):
    # 1. Instanciar o formulário com os dados de filtro
    form = EscolaSelectForm(request.GET)
    escola_nome_filtro = None
    titulo_sufixo = " - Visão Geral"
    
    if form.is_valid():
        escola_obj = form.cleaned_data.get('escola')
        if escola_obj:
            # Obtém o nome da escola para usar no filtro do Pandas
            escola_nome_filtro = escola_obj.nome 
            titulo_sufixo = f" - {escola_obj.nome}"
            
    context = {'form': form, 'titulo_sufixo': titulo_sufixo}
    
    try:
        df = pd.read_excel('dados_escolas.xlsx')
        
        # 2. Aplicar a Filtragem no DataFrame
        if escola_nome_filtro:
            # Filtra o DataFrame pela coluna 'Escola'
            df_filtrado = df[df['Escola'] == escola_nome_filtro]
        else:
            # Usa o DataFrame completo
            df_filtrado = df

        # 3. Gerar as Análises com o DataFrame Filtrado
        
        # Registros por Escola (Mostra apenas a escola filtrada ou o total de todas se não houver filtro)
        if escola_nome_filtro:
             # Para uma escola específica, apenas exibe a contagem total de registros
             contagem_registros = pd.Series({'Total de Registros': len(df_filtrado)}).to_frame().to_html(classes='table table-striped')
        else:
             # Visão Geral: Contagem por todas as escolas
             contagem_registros = df_filtrado['Escola'].value_counts().to_frame().to_html(classes='table table-striped')

        # Média do IDEB por Escola
        if escola_nome_filtro:
             # Para uma escola específica, apenas exibe a média do IDEB dela
             media_ideb_data = df_filtrado.groupby('Escola')['IDEB'].mean().to_frame().to_html(classes='table table-striped', header=['Média do IDEB'])
        else:
             # Visão Geral: Média do IDEB de todas as escolas
             media_ideb_data = df_filtrado.groupby('Escola')['IDEB'].mean().to_frame().to_html(classes='table table-striped', header=['Média do IDEB'])

        context.update({
            'analise_escola': contagem_registros, # Use o dado de contagem apropriado
            'media_ideb': media_ideb_data,
        })
        
    except FileNotFoundError:
        context['erro'] = "O arquivo 'dados_escolas.xlsx' não foi encontrado. Verifique o caminho."
    except Exception as e:
        context['erro'] = f"Ocorreu um erro ao processar os dados: {e}"

    return render(request, 'analise_dashboard.html', context)