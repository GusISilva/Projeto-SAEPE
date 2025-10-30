#!/bin/bash
set -e

echo "Instalando dependências..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput

echo "Build concluído com sucesso!"
