@echo off
cd /d "C:\caminho\para\sysPCP"
call venv\Scripts\activate
flask run --host=0.0.0.0 --port=5065