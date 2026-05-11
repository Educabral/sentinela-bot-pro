import os
from dotenv import load_dotenv

# Carrega as configurações do arquivo .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def check_configs():
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "sua_chave_do_telegram_aqui":
        print("⚠️ ERRO: Chave do Telegram não encontrada!")
        print("Abra o arquivo .env e coloque o token do seu bot em TELEGRAM_BOT_TOKEN.")
        exit(1)

    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "sua_chave_deepseek_aqui":
        print("⚠️ ERRO: Chave do DeepSeek não encontrada!")
        print("Abra o arquivo .env e coloque a sua chave em DEEPSEEK_API_KEY.")
        exit(1)
