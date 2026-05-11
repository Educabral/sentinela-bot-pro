#!/bin/bash
clear
echo "========================================================"
echo "   PASSO 3 - INSTALANDO O SENTINELA BOT"
echo "========================================================"
echo ""

# Navega para a pasta sistema onde estão os arquivos do bot
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/sistema"

# Verifica se o Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado!"
    echo "Volte e execute primeiro o arquivo: 2_INSTALAR_PYTHON.sh"
    echo ""
    read -p "Pressione ENTER para fechar..."
    exit 1
fi

echo "[1/3] Criando ambiente isolado do bot..."
python3 -m venv venv
echo "  OK!"
echo ""

echo "[2/3] Instalando bibliotecas necessárias (pode demorar)..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  OK!"
echo ""

echo "[3/3] Configurando permissões..."
cd "$SCRIPT_DIR"
chmod +x 4_INICIAR.sh
echo "  OK!"
echo ""

echo "========================================================"
echo "  PASSO 3 CONCLUÍDO! BOT INSTALADO COM SUCESSO!"
echo "========================================================"
echo ""
echo "Agora clique duas vezes no arquivo:"
echo "  4_INICIAR.sh"
echo ""
read -p "Pressione ENTER para fechar..."
