import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from config import TELEGRAM_BOT_TOKEN
from deepseek_brain import chat_with_deepseek, evaluate_opportunity
from data_fetcher import check_price_drops, scan_for_opportunities_sync
import time

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

ADMIN_CHAT_ID = None
alert_cooldowns = {}

async def monitor_market():
    """Roda em background verificando o mercado a cada 30 minutos."""
    global ADMIN_CHAT_ID
    while True:
        await asyncio.sleep(1800) # 30 minutos
        if ADMIN_CHAT_ID:
            print("[RADAR] Iniciando varredura das Top 100 moedas...")
            
            # Checagem rapida de drops
            alerts = await check_price_drops()
            for alert in alerts:
                try:
                    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=alert)
                except Exception as e:
                    print(f"Erro ao enviar alerta de drop: {e}")
                    
            # Scanner Ativo de Oportunidades SMC
            ops = await asyncio.to_thread(scan_for_opportunities_sync)
            print(f"[RADAR] {len(ops)} setups matematicos encontrados. Avaliando com a IA...")
            
            current_time = time.time()
            for op in ops:
                try:
                    symbol = op.split("ATIVO: ")[1].split("\n")[0].strip()
                    
                    # Cooldown de 4 horas por moeda
                    if symbol in alert_cooldowns and current_time - alert_cooldowns[symbol] < 14400:
                        continue
                        
                    ai_verdict = await evaluate_opportunity(op)
                    if ai_verdict:
                        alert_cooldowns[symbol] = current_time
                        msg = f"🎯 **RADAR SMC ATIVO** 🎯\n\n{ai_verdict}"
                        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
                        await asyncio.sleep(2) # Pausa para nao levar block do Telegram
                except Exception as e:
                    print(f"[ERRO NO RADAR]: {e}")

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = message.chat.id
    
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    resposta = await chat_with_deepseek("O usuario acabou de iniciar o chat. Faca uma apresentacao rapida. Lembre-se de sua personalidade de analista de alto nivel.", message.chat.id)
    await message.answer(resposta)

@dp.message(F.text)
async def handle_normal_messages(message: types.Message):
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = message.chat.id
    
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    resposta = await chat_with_deepseek(message.text, message.chat.id)
    
    await message.answer(resposta)

async def start_telegram_bot():
    print("[TELEGRAM] Bot online! Cerebro DeepSeek conectado.")
    asyncio.create_task(monitor_market())
    await dp.start_polling(bot)
