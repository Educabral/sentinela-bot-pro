@echo off
color 0A
title Instalador - SENTINELA Bot SMC
echo ========================================================
echo   INSTALANDO O SENTINELA - TRADING BOT PRO SMC
echo ========================================================
echo.

:: Verifica Python
echo [1/4] Verificando Python 3...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo [AVISO] Python nao encontrado! Baixando instalador automaticamente...
        echo.
        :: Baixa o instalador do Python 3.11 da Microsoft
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe'"
        echo [INFO] Instalando Python... (marque a opcao Add to PATH!)
        start /wait python_installer.exe InstallAllUsers=0 PrependPath=1 Include_test=0
        del python_installer.exe
        echo.
        echo [INFO] Python instalado! Continuando a instalacao do Bot...
        echo.
    )
)

:: Determina o executavel correto
python --version >nul 2>&1
if %errorlevel% equ 0 (set PYTHON=python) else (set PYTHON=py)

echo   OK! Python encontrado.
echo.

:: Cria o ambiente virtual
echo [2/4] Criando ambiente virtual isolado...
%PYTHON% -m venv venv
echo   OK! Ambiente criado.
echo.

:: Instala pacotes
echo [3/4] Instalando bibliotecas (pode demorar alguns minutos)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip uninstall -y aiodns pycares >nul 2>&1
echo   OK! Bibliotecas instaladas.
echo.

echo [4/4] Finalizando...
echo   OK!
echo.

echo ========================================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================================
echo.
echo PROXIMO PASSO:
echo   1. Renomeie o arquivo '.env.exemplo' para '.env'
echo   2. Abra o .env com o Bloco de Notas
echo   3. Coloque seu Token do Telegram e chave DeepSeek
echo   4. Depois, de dois cliques em 'iniciar.bat'
echo.
pause
