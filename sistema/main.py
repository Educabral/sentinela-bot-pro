import asyncio
import os
from aiohttp import web
from config import check_configs
from bot_telegram import start_telegram_bot

async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[NUVEM] Servidor Web iniciado na porta {port}")

async def main():
    print("=========================================")
    print("🚀 Iniciando Trading Bot Pro...")
    print("=========================================")
    
    # 1. Verifica se o comprador (ou você) preencheu as chaves no .env
    check_configs()
    
    # 2. Inicia o servidor web (obrigatório para plataformas gratuitas como Render)
    await start_web_server()
    
    # 3. Inicia o robô do telegram
    await start_telegram_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Bot desligado.")
