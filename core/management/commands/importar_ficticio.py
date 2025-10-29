# Em core/management/commands/importar_ficticio.py

import pandas as pd
from django.core.management.base import BaseCommand
from core.models import DadosFicticiosEscola # IMPORTA NOSSO NOVO MODELO

class Command(BaseCommand):
    help = 'Importa os dados Fictícios de Acompanhamento das Escolas'

    def handle(self, *args, **options):
        # --- MUDANÇA 1: Corrigimos o nome do arquivo ---
        caminho_excel = r'C:\Users\Rhydrian\Documents\Projeto-SAEPE\Acompanhamento_Escolas_2025_Ficticio.xlsx'

        self.stdout.write(f'Lendo o arquivo Excel de {caminho_excel}...')
        
        try:
            # --- MUDANÇA 2: Usamos pd.read_excel ---
            # O read_excel já entende que o cabeçalho está na primeira linha
            df = pd.read_excel(caminho_excel) 
            df = df.where(pd.notnull(df), None) # Limpa valores vazios
        
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('ERRO: Arquivo Excel não encontrado! Verifique o caminho e o nome do arquivo.'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao ler o Excel (verifique se openpyxl está instalado): {e}'))
            return

        # 2. LIMPE O BANCO DE DADOS ANTIGO
        self.stdout.write('Limpando dados fictícios antigos...')
        DadosFicticiosEscola.objects.all().delete()

        self.stdout.write('Iniciando a importação dos dados para o banco...')
        
        # 3. PERCORRA O ARQUIVO E SALVE NO BANCO (este código continua igual)
        for _, row in df.iterrows():
            try:
                DadosFicticiosEscola.objects.create(
                    # model_field = row['NOME DA COLUNA NO CSV']
                    escola = row['ESCOLA'],
                    modalidade = row['MODALIDADE'],
                    alunos_previstos_2023 = row['ALUNOS PREVISTOS SAEPE 2023'],
                    percentual_peso = row['% PESO'],
                    saepe_2022 = row['SAEPE 2022'],
                    saepe_2023 = row['SAEPE 2023'],
                    proficiencia_lp_2023 = row['PROFICIÊNCIA LP SAEPE 2023'],
                    proficiencia_mt_2023 = row['PROFICIÊNCIA MT SAEPE 2023'],
                    matricula_efaf_2024 = row['MATRÍCULA EFAF 2024']
                )
            except Exception as e:
                self.stderr.write(f'Erro ao importar linha: {e} - Dados: {row}')

        self.stdout.write(self.style.SUCCESS('Importação fictícia concluída com sucesso!'))