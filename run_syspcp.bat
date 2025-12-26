@echo off
setlocal

REM === AJUSTE AQUI O CAMINHO DO PROJETO ===
set "PROJECT_DIR=C:\sysPCP"

REM === REDE/PORTA ===
set "HOST=0.0.0.0"
set "PORT=5050"

REM === OPCIONAL: LOGS ===
set "LOG_DIR=%PROJECT_DIR%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set "LOG_FILE=%LOG_DIR%\waitress.log"

REM === VÁ PARA A PASTA DO PROJETO ===
cd /d "%PROJECT_DIR%"

REM === (OPCIONAL) GARANTA VARIAVEIS DE AMBIENTE DO APP ===
REM set "FLASK_ENV=production"
REM set "PYTHONIOENCODING=utf-8"

REM === CHAME O EXECUTÁVEL DO WAITRESS DO VENV (NÃO PRECISA ATIVAR O VENV) ===
"%PROJECT_DIR%\venv\Scripts\waitress-serve.exe" --host=%HOST% --port=%PORT% wsgi:app >> "%LOG_FILE%" 2>&1
