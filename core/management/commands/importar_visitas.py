# Em core/management/commands/importar_visitas.py

import pandas as pd
from django.core.management.base import BaseCommand
from core.models import VisitaTecnica # Importa o nosso novo modelo

class Command(BaseCommand):
    help = 'Importa as Visitas Técnicas do ficheiro Excel corrigido.'

    def handle(self, *args, **options):
        
        # 1. CAMINHO DO SEU FICHEIRO EXCEL CORRIGIDO
        caminho_excel = r'C:\Users\Rhydrian\Documents\Projeto-SAEPE\visitas_gre_ficticias.xlsx'

        self.stdout.write(f'A ler o ficheiro Excel de {caminho_excel}...')
        
        try:
            # Usamos read_excel. O cabeçalho está na primeira linha (header=0), que é o padrão.
            df = pd.read_excel(caminho_excel, engine='openpyxl')
            # Limpa valores vazios (como NaN) para None, que o banco de dados aceita
            df = df.where(pd.notnull(df), None)
        
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('ERRO: Ficheiro Excel não encontrado! Verifique o caminho.'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao ler o Excel: {e}'))
            return

        # 2. LIMPA O BANCO DE DADOS ANTIGO (para não duplicar dados)
        self.stdout.write('A limpar visitas técnicas antigas...')
        VisitaTecnica.objects.all().delete()

        self.stdout.write('A iniciar a importação das visitas para o banco de dados...')
        
        # 3. PERCORRE O FICHEIRO E SALVA NO BANCO
        for _, row in df.iterrows():
            try:
                # Converte datas se não estiverem no formato correto (o Excel às vezes guarda como timestamp)
                data_visita = pd.to_datetime(row['Data da Visita']).date() if row['Data da Visita'] else None

                VisitaTecnica.objects.create(
                    # campo_do_modelo = row['NOME_EXATO_DA_COLUNA_NO_EXCEL']
                    escola = row['Escola'],
                    data_visita = data_visita,
                    tecnico_gre = row['Técnico/Analista - GRE'],
                    servidor_escola = row['Servidor da Escola'],
                    demanda = row['Demanda'],
                    encaminhamento = row['Encaminhamento'],
                    observacao = row['Observação']
                )
            except Exception as e:
                # Se der erro, ele vai dizer qual linha falhou
                self.stderr.write(f'Erro ao importar linha: {e} - Dados: {row}')

        self.stdout.write(self.style.SUCCESS('Importação de visitas técnicas concluída com sucesso!'))