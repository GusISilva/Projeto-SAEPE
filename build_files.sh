#!/bin/bash
set -e

# Ativa o ambiente virtual se você estiver usando
# source venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Build concluído com sucesso!"
