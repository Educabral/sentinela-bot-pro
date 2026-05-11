#!/bin/bash
cd "$(dirname "$0")"
clear
echo "========================================================"
echo "   INSTALANDO O TRADING BOT PRO SMC - macOS / Apple"
echo "========================================================"
echo ""

echo "[1/4] Verificando Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 nao foi encontrado no seu Mac!"
    echo "Baixe e instale o Python oficial: https://www.python.org/downloads/macos/"
    exit 1
fi
echo "  OK! Python 3 encontrado."
echo ""

echo "[2/4] Criando ambiente virtual..."
python3 -m venv venv
echo "  OK! Ambiente criado."
echo ""

echo "[3/4] Instalando bibliotecas necessarias..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  OK! Todas as bibliotecas instaladas."
echo ""

echo "[4/4] Configurando permissoes..."
chmod +x iniciar_mac.command
echo "  OK!"
echo ""

echo "========================================================"
echo "  INSTALACAO CONCLUIDA COM SUCESSO!"
echo "========================================================"
echo ""
echo "PROXIMO PASSO:"
echo "  1. Renomeie o arquivo '.env.exemplo' para '.env'"
echo "  2. Coloque suas chaves no arquivo"
echo "  3. Depois, apenas de DOIS CLIQUES no arquivo 'iniciar_mac.command'"
echo ""
read -p "Pressione ENTER para fechar essa janela..."
