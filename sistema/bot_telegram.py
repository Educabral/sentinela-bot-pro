import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from config import TELEGRAM_BOT_TOKEN
from deepseek_brain import chat_with_deepseek, evaluate_opportunity
from data_fetcher import check_price_drops, scan_for_opportunities_sync
import time
from datetime import datetime

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

ADMIN_CHAT_ID = None
alert_cooldowns = {}

# === CONTROLE DE VOLUME ===
SCAN_INTERVAL = 7200        # 2 horas entre scans (era 30 min)
COOLDOWN_PER_COIN = 28800   # 8 horas de cooldown por moeda (era 4h)
MAX_ALERTS_PER_CYCLE = 5    # Maximo de alertas enviados por ciclo de scan
MAX_ALERTS_PER_DAY = 15     # Maximo de alertas por dia
daily_alert_count = 0
last_reset_day = datetime.now().day

async def monitor_market():
    """Roda em background verificando o mercado a cada 2 horas."""
    global ADMIN_CHAT_ID, daily_alert_count, last_reset_day
    while True:
        await asyncio.sleep(SCAN_INTERVAL)
        if ADMIN_CHAT_ID:
            # Reset do contador diario a meia-noite
            today = datetime.now().day
            if today != last_reset_day:
                daily_alert_count = 0
                last_reset_day = today
                print(f"[RADAR] Novo dia detectado. Contador de alertas resetado.")
            
            # Verifica se ja atingiu o limite diario
            if daily_alert_count >= MAX_ALERTS_PER_DAY:
                print(f"[RADAR] Limite diario de {MAX_ALERTS_PER_DAY} alertas atingido. Proximo scan em {SCAN_INTERVAL//3600}h.")
                continue
            
            print(f"[RADAR] Iniciando varredura... ({daily_alert_count}/{MAX_ALERTS_PER_DAY} alertas hoje)")
            
            # Checagem rapida de drops (apenas quedas bruscas, nao conta no limite)
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
            alerts_this_cycle = 0
            
            for op in ops:
                # Limite por ciclo
                if alerts_this_cycle >= MAX_ALERTS_PER_CYCLE:
                    print(f"[RADAR] Limite de {MAX_ALERTS_PER_CYCLE} alertas por ciclo atingido. Restante ignorado.")
                    break
                
                # Limite diario
                if daily_alert_count >= MAX_ALERTS_PER_DAY:
                    print(f"[RADAR] Limite diario de {MAX_ALERTS_PER_DAY} alertas atingido.")
                    break
                
                try:
                    symbol = op.split("ATIVO: ")[1].split("\n")[0].strip()
                    
                    # Cooldown de 8 horas por moeda
                    if symbol in alert_cooldowns and current_time - alert_cooldowns[symbol] < COOLDOWN_PER_COIN:
                        continue
                        
                    ai_verdict = await evaluate_opportunity(op)
                    if ai_verdict:
                        alert_cooldowns[symbol] = current_time
                        daily_alert_count += 1
                        alerts_this_cycle += 1
                        msg = f"🎯 RADAR SMC ATIVO 🎯\n\n{ai_verdict}"
                        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
                        await asyncio.sleep(5) # Pausa de 5s entre alertas
                except Exception as e:
                    print(f"[ERRO NO RADAR]: {e}")
            
            print(f"[RADAR] Ciclo finalizado. {alerts_this_cycle} alertas enviados. Total hoje: {daily_alert_count}/{MAX_ALERTS_PER_DAY}")

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
