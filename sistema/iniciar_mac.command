#!/bin/bash
cd "$(dirname "$0")"
clear
echo "========================================================"
echo "          INICIANDO O TRADING BOT PRO SMC"
echo "========================================================"
echo ""

if [ ! -d "venv" ]; then
    echo "[ERRO] Ambiente virtual nao encontrado!"
    echo "Por favor, rode o arquivo 'instalar_mac.command' primeiro."
    read -p "Pressione ENTER para sair..."
    exit 1
fi

source venv/bin/activate
python3 main.py

read -p "O bot foi encerrado. Pressione ENTER para sair..."
