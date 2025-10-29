# core/views.py

import pandas as pd
import json
import os 
from django.conf import settings 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Max, Count
from django.db import IntegrityError 


from .models import Escola, Ocorrencia, Relatorio, Visita, DadosFicticiosEscola, VisitaTecnica
from .forms import VisitaForm, EscolaSelectForm, VisitaTecnicaForm


# ==============================================================================
# FUNÇÃO AUXILIAR: CARREGAR CSV (APENAS PARA TESTES/DEV)
# ==============================================================================

# ATENÇÃO: Descomente e use APENAS UMA VEZ para carregar seus dados no banco.
# Em produção, você deve remover a chamada dessa função e carregar os dados uma única vez.
def carregar_dados_csv_para_modelos():
    """Tenta carregar os dados dos arquivos CSV para os modelos, se ainda não existirem."""
    
    # 1. Carregar DadosFicticiosEscola (Acompanhamento)
    caminho_escolas_csv = os.path.join(settings.BASE_DIR, 'Acompanhamento_Escolas_2025_Ficticio.xlsx - Sheet1.csv')
    if not DadosFicticiosEscola.objects.exists() and os.path.exists(caminho_escolas_csv):
        print("Tentando carregar dados de Acompanhamento_Escolas...")
        try:
            df_escolas = pd.read_csv(caminho_escolas_csv)
            # Normalizar nomes de colunas do CSV para os nomes do modelo
            df_escolas.columns = [
                'escola', 'modalidade', 'alunos_previstos_2023', 'percentual_peso', 
                'saepe_2022', 'saepe_2023', 'proficiencia_lp_2023', 'proficiencia_mt_2023', 
                'matricula_efaf_2024'
            ]
            
            for index, row in df_escolas.iterrows():
                DadosFicticiosEscola.objects.create(
                    escola=row['escola'],
                    modalidade=row['modalidade'],
                    alunos_previstos_2023=row['alunos_previstos_2023'],
                    percentual_peso=row['percentual_peso'],
                    saepe_2022=row['saepe_2022'],
                    saepe_2023=row['saepe_2023'],
                    proficiencia_lp_2023=row['proficiencia_lp_2023'],
                    proficiencia_mt_2023=row['proficiencia_mt_2023'],
                    matricula_efaf_2024=row['matricula_efaf_2024']
                )
            print("Dados de Acompanhamento de Escolas carregados.")
        except Exception as e:
            print(f"Erro ao carregar dados de Acompanhamento: {e}")

    # 2. Carregar VisitaTecnica
    caminho_visitas_csv = os.path.join(settings.BASE_DIR, 'visitas_gre_ficticias.xlsx - Sheet1.csv')
    if not VisitaTecnica.objects.exists() and os.path.exists(caminho_visitas_csv):
        print("Tentando carregar dados de Visitas Tecnicas...")
        try:
            df_visitas = pd.read_csv(caminho_visitas_csv)
            
            for index, row in df_visitas.iterrows():
                VisitaTecnica.objects.create(
                    escola=row['Escola'],
                    data_visita=pd.to_datetime(row['Data da Visita'], errors='coerce').date(),
                    tecnico_gre=row['Técnico/Analista - GRE'],
                    servidor_escola=row['Servidor da Escola'],
                    demanda=row['Demanda'],
                    encaminhamento=row['Encaminhamento'],
                    observacao=row['Observação']
                )
            print("Dados de Visitas Técnicas carregados.")
        except Exception as e:
            print(f"Erro ao carregar dados de Visitas Técnicas: {e}")


# ==============================================================================
# VIEWS DE AUTENTICAÇÃO E DASHBOARD PRINCIPAL
# ==============================================================================

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
        context = {}
        return render(request, 'relatorios.html', context)


@login_required(login_url='login')
def visitas_view(request):

    # --- Lógica de POST (Processa o formulário do popup) ---
    if request.method == 'POST':
        form = VisitaTecnicaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Visita registada com sucesso!')
                return redirect('visitas')
            except IntegrityError as e:
                messages.error(request, f'Erro de integridade ao guardar a visita: {e}')
            except Exception as e:
                 messages.error(request, f'Erro inesperado ao guardar a visita: {e}')
        else:
            error_message = 'Erro ao guardar. Por favor, verifique os dados: '
            for field, errors in form.errors.items():
                label = form.fields[field].label if field in form.fields else field
                error_message += f"'{label}': {', '.join(errors)} "
            messages.error(request, error_message.strip())

    # --- Lógica de GET (Mostra o resumo das últimas visitas) ---

    # 1. Encontra a data da última visita para cada escola
    ultimas_visitas_por_escola = VisitaTecnica.objects.values(
        'escola' 
    ).annotate(
        ultima_data=Max('data_visita') 
    ) 

    # 2. Busca os detalhes completos da última visita de cada escola
    lista_resumo_visitas = []
    for item in ultimas_visitas_por_escola:
        try:
            # Encontra a visita mais recente (maior ID) na última data para evitar duplicatas
            ultima_visita_obj = VisitaTecnica.objects.filter(
                escola=item['escola'],
                data_visita=item['ultima_data']
            ).latest('id') 
            lista_resumo_visitas.append(ultima_visita_obj)
        except VisitaTecnica.DoesNotExist:
            continue
            
    # 3. Ordena a LISTA de objetos pelo atributo 'escola' (alfabeticamente)
    lista_resumo_visitas.sort(key=lambda visita: visita.escola)

    # 4. Cria uma instância VAZIA do formulário para o popup
    form_modal = VisitaTecnicaForm()

    # 5. Monta o contexto para o template
    context = {
        'form_modal': form_modal,           
        'resumo_visitas': lista_resumo_visitas,
    }

    return render(request, 'visitas.html', context)




@login_required(login_url='login')
def analise_dashboard_view(request):
    
    
    form = EscolaSelectForm(request.GET or None) 
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
    dados_grafico_json = '{}' 
    dados_grafico_visitas_json = '{}' 
    tabela_1_html = "<p>Nenhum dado encontrado.</p>"
    tabela_2_html = "<p>Nenhum dado encontrado.</p>"
    
    try:
        # --- 1. Lógica para Gráfico de Barras e Tabelas (Desempenho) ---
        base_query = DadosFicticiosEscola.objects.all()

        if escola_nome_filtro:
            base_query = base_query.filter(escola=escola_nome_filtro)

        # Dados para Tabela e Barras
        dados_tabelas = list(base_query.values(
            'escola', 'saepe_2022', 'saepe_2023', 
            'proficiencia_lp_2023', 'proficiencia_mt_2023'
        ))

        # Geração do JSON do Gráfico de Barras
        if dados_tabelas:
            # Se for uma única escola, mostra as métricas dela
            if escola_nome_filtro:
                escola_info = dados_tabelas[0]
                dados_grafico = {
                    'labels': ['SAEPE 2022', 'SAEPE 2023', 'LP 2023', 'MT 2023'],
                    'datasets': [{
                        'label': escola_info['escola'],
                        'data': [
                            escola_info['saepe_2022'], 
                            escola_info['saepe_2023'], 
                            escola_info['proficiencia_lp_2023'], 
                            escola_info['proficiencia_mt_2023']
                        ],
                        'backgroundColor': 'rgba(75, 192, 192, 0.7)',
                        'borderColor': 'rgba(75, 192, 192, 1)',
                        'borderWidth': 1
                    }]
                }
            # Se for Visão Geral, mostra um comparativo (ex: Top 5 Proficiência)
            else:
                top_escolas = sorted(dados_tabelas, key=lambda x: x['proficiencia_lp_2023'], reverse=True)[:5]
                labels = [e['escola'] for e in top_escolas]
                data_lp = [e['proficiencia_lp_2023'] for e in top_escolas]
                data_mt = [e['proficiencia_mt_2023'] for e in top_escolas]
                
                dados_grafico = {
                    'labels': labels,
                    'datasets': [
                        {'label': 'Proficiência LP 2023', 'data': data_lp, 'backgroundColor': 'rgba(54, 162, 235, 0.7)'},
                        {'label': 'Proficiência MT 2023', 'data': data_mt, 'backgroundColor': 'rgba(255, 99, 132, 0.7)'}
                    ]
                }

            dados_grafico_json = json.dumps(dados_grafico)
            
            # Geração das Tabelas HTML
            for item in dados_tabelas:
                try:
                    url_perfil = reverse('perfil_escola', args=[item['escola']])
                    item['escola_link'] = format_html('<a href="{}">{}</a>', url_perfil, item['escola'])
                except Exception as link_error:
                    item['escola_link'] = item['escola'] 
                    print(f"Erro ao gerar link para {item['escola']}: {link_error}")

            df_tabelas = pd.DataFrame(dados_tabelas)
            
            tabela_1_html = df_tabelas[['escola_link', 'saepe_2022', 'saepe_2023']].rename(
                columns={'escola_link': 'Escola', 'saepe_2022': 'SAEPE 2022', 'saepe_2023': 'SAEPE 2023'}
            ).to_html(classes='table table-striped table-hover', index=False, escape=False)
            
            tabela_2_html = df_tabelas[['escola_link', 'proficiencia_lp_2023', 'proficiencia_mt_2023']].rename(
                columns={'escola_link': 'Escola', 'proficiencia_lp_2023': 'Proficiência LP 2023', 'proficiencia_mt_2023': 'Proficiência MT 2023'}
            ).to_html(classes='table table-striped table-hover', index=False, escape=False)
        else:
            # Caso não haja dados de escola
            dados_grafico_json = '{}'

        # --- 2. Lógica para Gráfico de Rosca (Visitas por Técnico) ---
        visitas_por_tecnico = VisitaTecnica.objects.values('tecnico_gre').annotate(total=Count('id')).order_by('-total')
        
        labels_visitas = [item['tecnico_gre'] for item in visitas_por_tecnico]
        data_visitas = [item['total'] for item in visitas_por_tecnico]

        cores_fundo = [
            'rgba(255, 99, 132, 0.7)', 
            'rgba(54, 162, 235, 0.7)',  
            'rgba(255, 206, 86, 0.7)',  
            'rgba(75, 192, 192, 0.7)',  
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)', 
            'rgba(199, 199, 199, 0.7)',
        ]
        
        dados_grafico_visitas = {
            'labels': labels_visitas,
            'datasets': [{
                'label': 'Número de Visitas',
                'data': data_visitas,
                'backgroundColor': cores_fundo[:len(labels_visitas)],
                'borderColor': [c.replace('0.7', '1') for c in cores_fundo[:len(labels_visitas)]],
                'borderWidth': 1
            }]
        }
        dados_grafico_visitas_json = json.dumps(dados_grafico_visitas)


    except Exception as e:
        erro = f"Ocorreu um erro ao consultar os dados: {e}"
        # Reseta todos os JSONs em caso de erro
        dados_grafico_json = '{}'
        dados_grafico_visitas_json = '{}'
        tabela_1_html = f"<p>Erro ao carregar dados: {e}</p>"
        tabela_2_html = f"<p>Erro ao carregar dados: {e}</p>"

    context = {
        'form': form, 
        'titulo_sufixo': titulo_sufixo,
        'erro': erro,
        'dados_grafico_json': dados_grafico_json,
        'dados_grafico_visitas_json': dados_grafico_visitas_json,
        'analise_escola': tabela_1_html, 
        'media_ideb': tabela_2_html,    
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
    

@login_required(login_url='login')
def main_dashboard_view(request):
    
    total_escolas = DadosFicticiosEscola.objects.values('escola').distinct().count()
    total_visitas = VisitaTecnica.objects.count()
    relatorios_pendentes = VisitaTecnica.objects.exclude(encaminhamento__gt='').count()
    ultima_visita_obj = VisitaTecnica.objects.aggregate(Max('data_visita'))
    ultima_data_visita = ultima_visita_obj.get('data_visita__max')
    context = {
        'total_escolas': total_escolas,
        'total_visitas': total_visitas,
        'relatorios_pendentes': relatorios_pendentes,
        'ultima_data_visita': ultima_data_visita, 
    }

    return render(request, 'main_dashboard.html', context)


@login_required(login_url='login')
def main_dashboard_view(request):
    try:
        # 1. Total de Escolas (contando escolas distintas nos DadosFicticiosEscola)
        total_escolas = DadosFicticiosEscola.objects.values('escola').distinct().count()

        # 2. Visitas Concluídas (total de registros em VisitaTecnica)
        total_visitas = VisitaTecnica.objects.count()

        # 3. Relatórios Pendentes (Visitas onde 'encaminhamento' está vazio ou nulo)
        # O campo 'encaminhamento' tem 'null=True, blank=True' no models.py
        relatorios_pendentes = VisitaTecnica.objects.filter(encaminhamento__in=['', None]).count()

        # 4. Última Visita (data máxima de visita)
        ultima_visita_obj = VisitaTecnica.objects.aggregate(max_date=Max('data_visita'))
        ultima_data_visita = ultima_visita_obj.get('max_date') # Pode ser None se não houver visitas

    except Exception as e:
        # Em caso de erro (ex: banco de dados vazio/desconectado), define valores padrão
        print(f"Erro ao carregar métricas: {e}")
        total_escolas = 0
        total_visitas = 0
        relatorios_pendentes = 0
        ultima_data_visita = None # ou "N/A" se preferir passar uma string

    context = {
        'total_escolas': total_escolas,
        'total_visitas': total_visitas,
        'relatorios_pendentes': relatorios_pendentes,
        'ultima_data_visita': ultima_data_visita,
    }

    return render(request, 'main_dashboard.html', context)