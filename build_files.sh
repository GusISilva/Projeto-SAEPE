#!/bin/bash
set -e

python -m pip install --upgrade pip
python -m pip install -r requirements.txt


echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Build concluído com sucesso!"
