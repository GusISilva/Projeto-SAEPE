@echo off
title Iniciar Servidor Django

echo Ativando o ambiente virtual...
call venv\Scripts\activate

echo Instalando dependencias (se ja instaladas, sera pulado)...
pip install -r requirements.txt

echo Aplicando migrações...
python manage.py migrate

echo Iniciando o servidor de desenvolvimento...
echo Acesse: http://127.0.0.1:8000/
python manage.py runserver

pause