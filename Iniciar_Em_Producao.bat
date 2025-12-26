@echo off
cd /d "C:\caminho\para\sysPCP"
call venv\Scripts\activate
waitress-serve --host=0.0.0.0 --port=5065 wsgi:app