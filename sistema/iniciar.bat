@echo off
title SENTINELA - Bot SMC
color 0A

echo ==============================================
echo        Iniciando o SENTINELA - Bot SMC
echo ==============================================
echo.

:: Verifica se o venv existe
if not exist "venv\" (
    echo [ERRO] Ambiente nao encontrado!
    echo Execute o arquivo 'instalar.bat' primeiro.
    echo.
    pause
    exit /b
)

:: Verifica se o .env existe
if not exist ".env" (
    echo [ERRO] Arquivo .env nao encontrado!
    echo Renomeie o arquivo '.env.exemplo' para '.env' e adicione suas chaves.
    echo.
    pause
    exit /b
)

echo [INFO] Verificando dependencias...
call venv\Scripts\activate
pip install -r requirements.txt --quiet
pip uninstall -y aiodns pycares >nul 2>&1

echo [INFO] Iniciando o SENTINELA...
echo.
echo ==============================================
echo  Para parar o bot, feche esta janela
echo ==============================================
echo.
python main.py

pause
