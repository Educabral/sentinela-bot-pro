#!/bin/bash
clear
echo "========================================================"
echo "        Iniciando o SENTINELA - Bot SMC"
echo "========================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/sistema"

# Verifica se o bot foi instalado
if [ ! -d "venv" ]; then
    echo "[ERRO] Bot não instalado!"
    echo "Execute primeiro o arquivo: 3_INSTALAR_BOT.sh"
    echo ""
    read -p "Pressione ENTER para fechar..."
    exit 1
fi

# Verifica se o .env existe
if [ ! -f ".env" ]; then
    echo "[ERRO] Arquivo de configuração não encontrado!"
    echo "Entre em contato com o suporte."
    echo ""
    read -p "Pressione ENTER para fechar..."
    exit 1
fi

echo "[INFO] Ativando o sistema..."
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "[INFO] Iniciando o SENTINELA..."
echo ""
echo "========================================================"
echo "  Bot online! Abra o Telegram e envie /start"
echo "  Para parar o bot: pressione CTRL + C"
echo "========================================================"
echo ""
python3 main.py
