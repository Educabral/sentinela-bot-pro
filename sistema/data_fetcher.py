import ccxt
import pandas as pd
import numpy as np

exchange = ccxt.bybit()

print("[SISTEMA] Conectando na Exchange (Bybit) e carregando todas as moedas...")
try:
    markets = exchange.load_markets()
    valid_symbols = [symbol.split('/')[0] for symbol in markets.keys() if symbol.endswith('/USDT')]
    valid_symbols_lower = {s.lower(): s for s in valid_symbols}
    valid_symbols_lower["bitcoin"] = "BTC"
    valid_symbols_lower["ethereum"] = "ETH"
    valid_symbols_lower["binance coin"] = "BNB"
    valid_symbols_lower["cardano"] = "ADA"
    valid_symbols_lower["lido"] = "LDO"
    valid_symbols_lower["polygon"] = "MATIC"
    valid_symbols_lower["chainlink"] = "LINK"
    valid_symbols_lower["avalanche"] = "AVAX"
    valid_symbols_lower["polkadot"] = "DOT"
    valid_symbols_lower["ripple"] = "XRP"
    valid_symbols_lower["dogecoin"] = "DOGE"
    valid_symbols_lower["shiba inu"] = "SHIB"
    valid_symbols_lower["shiba"] = "SHIB"
    valid_symbols_lower["pepe"] = "PEPE"
    valid_symbols_lower["optimism"] = "OP"
    valid_symbols_lower["arbitrum"] = "ARB"
    valid_symbols_lower["aptos"] = "APT"
    valid_symbols_lower["sui"] = "SUI"
    valid_symbols_lower["celestia"] = "TIA"
    valid_symbols_lower["injective"] = "INJ"
    valid_symbols_lower["render"] = "RNDR"
    valid_symbols_lower["maker"] = "MKR"
    valid_symbols_lower["cosmos"] = "ATOM"
    valid_symbols_lower["litecoin"] = "LTC"
    valid_symbols_lower["uniswap"] = "UNI"
    print(f"[SISTEMA] {len(valid_symbols_lower)} pares USDT e sinônimos carregados com sucesso!")
except Exception as e:
    print(f"[ERRO] Falha ao carregar mercados da Binance: {e}")
    valid_symbols_lower = {"btc": "BTC", "bitcoin": "BTC", "eth": "ETH", "ethereum": "ETH", "sol": "SOL"}

def calculate_indicators(df):
    """Calcula todos os indicadores técnicos com pandas/numpy puro."""
    # --- RSI 14 ---
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df['RSI_14'] = 100 - (100 / (1 + rs))

    # --- EMA 9, 21, 200 ---
    df['EMA_9']  = df['close'].ewm(span=9,  adjust=False).mean()
    df['EMA_21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()

    # --- MACD (12, 26, 9) ---
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']

    # --- Bollinger Bands (20, 2) ---
    df['BB_mid']   = df['close'].rolling(window=20).mean()
    bb_std         = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_mid'] + (bb_std * 2)
    df['BB_lower'] = df['BB_mid'] - (bb_std * 2)
    df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_mid']

    # --- ATR 14 ---
    high_low   = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close  = (df['low']  - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR_14'] = tr.ewm(alpha=1/14, adjust=False).mean()

    # --- Stochastic RSI (14, 3, 3) ---
    rsi = df['RSI_14']
    rsi_min = rsi.rolling(window=14).min()
    rsi_max = rsi.rolling(window=14).max()
    stoch_rsi_raw = (rsi - rsi_min) / (rsi_max - rsi_min + 1e-9)
    df['StochRSI_K'] = stoch_rsi_raw.rolling(window=3).mean() * 100
    df['StochRSI_D'] = df['StochRSI_K'].rolling(window=3).mean()

    # --- VWAP (sessão completa disponível no df) ---
    df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

    # --- Volume SMA 20 ---
    df['vol_sma'] = df['volume'].rolling(window=20).mean()

    return df


def analyze_smc(df):
    """Retorna um dicionário com os conceitos SMC baseados no dataframe."""
    fvg_bullish = []
    fvg_bearish = []
    ob_bullish = []
    ob_bearish = []
    swing_highs = []
    swing_lows = []
    
    struct_df = df.tail(60).reset_index(drop=True)
    for i in range(2, len(struct_df)-2):
        if struct_df['high'].iloc[i] > struct_df['high'].iloc[i-1] and \
           struct_df['high'].iloc[i] > struct_df['high'].iloc[i-2] and \
           struct_df['high'].iloc[i] > struct_df['high'].iloc[i+1] and \
           struct_df['high'].iloc[i] > struct_df['high'].iloc[i+2]:
            swing_highs.append(struct_df['high'].iloc[i])
            
        if struct_df['low'].iloc[i] < struct_df['low'].iloc[i-1] and \
           struct_df['low'].iloc[i] < struct_df['low'].iloc[i-2] and \
           struct_df['low'].iloc[i] < struct_df['low'].iloc[i+1] and \
           struct_df['low'].iloc[i] < struct_df['low'].iloc[i+2]:
            swing_lows.append(struct_df['low'].iloc[i])
    
    recent_df = df.tail(20).reset_index(drop=True)
    
    for i in range(2, len(recent_df)-1):
        if recent_df['low'].iloc[i] > recent_df['high'].iloc[i-2]:
            gap = (recent_df['high'].iloc[i-2], recent_df['low'].iloc[i])
            filled = False
            for j in range(i+1, len(recent_df)):
                if recent_df['low'].iloc[j] < gap[1]:
                    filled = True
                    break
            if not filled:
                fvg_bullish.append(gap)
                
        if recent_df['high'].iloc[i] < recent_df['low'].iloc[i-2]:
            gap = (recent_df['high'].iloc[i], recent_df['low'].iloc[i-2])
            filled = False
            for j in range(i+1, len(recent_df)):
                if recent_df['high'].iloc[j] > gap[0]:
                    filled = True
                    break
            if not filled:
                fvg_bearish.append(gap)

    liquidity_high = recent_df['high'].max()
    liquidity_low  = recent_df['low'].min()
    
    avg_body = (recent_df['close'] - recent_df['open']).abs().mean()
    for i in range(1, len(recent_df)):
        body = abs(recent_df['close'].iloc[i] - recent_df['open'].iloc[i])
        if body > avg_body * 1.5:
            if recent_df['close'].iloc[i] > recent_df['open'].iloc[i]: 
                if recent_df['close'].iloc[i-1] < recent_df['open'].iloc[i-1]:
                    ob_bullish.append(recent_df['low'].iloc[i-1])
            else: 
                if recent_df['close'].iloc[i-1] > recent_df['open'].iloc[i-1]:
                    ob_bearish.append(recent_df['high'].iloc[i-1])
    
    return {
        "fvg_bullish": fvg_bullish[-1] if fvg_bullish else None,
        "fvg_bearish": fvg_bearish[-1] if fvg_bearish else None,
        "ob_bullish": ob_bullish[-1] if ob_bullish else None,
        "ob_bearish": ob_bearish[-1] if ob_bearish else None,
        "liquidity_high": liquidity_high,
        "liquidity_low": liquidity_low,
        "swing_highs": [round(x, 4) for x in swing_highs[-3:]] if swing_highs else [],
        "swing_lows": [round(x, 4) for x in swing_lows[-3:]] if swing_lows else []
    }

def get_live_market_context(user_message: str) -> str:
    msg_lower = user_message.lower().replace("?", " ").replace(",", " ").replace(".", " ")
    words = msg_lower.split()
    found_symbols = set()
    
    blacklist = {"dia", "bom", "ola", "uma", "ele", "ela", "tem", "vai", "vou", "que", "pra", "pro", "tia", "rei", "gas", "hot"}
    
    # Busca por palavras exatas
    for word in words:
        if len(word) > 1 and word not in blacklist and word in valid_symbols_lower:
            found_symbols.add(valid_symbols_lower[word])
            
    # Busca por nomes compostos (apenas chaves com espaco)
    if not found_symbols:
        for key, symbol in valid_symbols_lower.items():
            if " " in key and key in msg_lower:
                found_symbols.add(symbol)
                
    # NAO usar mais o fallback automático para BTC.
    # Se o usuário não pediu nenhuma moeda (ex: "bom dia", "obrigado"), o bot não puxa nada e só conversa.
        
    context_lines = []
    timeframes_to_check = ["4h", "1h", "15m", "5m"]
    
    for symbol in found_symbols:
        context_lines.append(f"ATIVO: {symbol}")
        try:
            for tf in timeframes_to_check:
                ohlcv = exchange.fetch_ohlcv(f"{symbol}/USDT", timeframe=tf, limit=220)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df = calculate_indicators(df)
                
                last = df.iloc[-1]
                prev = df.iloc[-2]
                price = last['close']

                # RSI
                rsi = last['RSI_14'] if not pd.isna(last['RSI_14']) else 50

                # EMAs
                ema9   = last['EMA_9']
                ema21  = last['EMA_21']
                ema200 = last['EMA_200']
                trend_curto  = "ALTA" if ema9 > ema21  else "BAIXA"
                trend_longo  = "ALTA" if price > ema200 else "BAIXA"

                # MACD
                macd_val  = last['MACD']
                macd_sig  = last['MACD_signal']
                macd_hist = last['MACD_hist']
                macd_cross = ""
                if prev['MACD'] < prev['MACD_signal'] and macd_val > macd_sig:
                    macd_cross = " [CRUZAMENTO ALTISTA]"
                elif prev['MACD'] > prev['MACD_signal'] and macd_val < macd_sig:
                    macd_cross = " [CRUZAMENTO BAIXISTA]"

                # Bollinger Bands
                bb_upper = last['BB_upper']
                bb_lower = last['BB_lower']
                bb_width = last['BB_width']
                bb_status = "SQUEEZE" if bb_width < df['BB_width'].quantile(0.2) else ("EXPANSAO" if bb_width > df['BB_width'].quantile(0.8) else "NORMAL")
                bb_pos = ""
                if price >= bb_upper * 0.999:
                    bb_pos = "tocando BANDA SUPERIOR"
                elif price <= bb_lower * 1.001:
                    bb_pos = "tocando BANDA INFERIOR"
                else:
                    bb_pos = f"dentro das bandas (sup:{bb_upper:.4f} inf:{bb_lower:.4f})"

                # ATR
                atr = last['ATR_14']
                atr_pct = (atr / price) * 100

                # Stoch RSI
                stoch_k = last['StochRSI_K'] if not pd.isna(last['StochRSI_K']) else 50
                stoch_d = last['StochRSI_D'] if not pd.isna(last['StochRSI_D']) else 50
                stoch_status = "SOBRECOMPRADO" if stoch_k > 80 else ("SOBREVENDIDO" if stoch_k < 20 else "NEUTRO")

                # VWAP
                vwap = last['VWAP']
                vwap_pos = "ACIMA do VWAP" if price > vwap else "ABAIXO do VWAP"

                # Volume
                vol_current = last['volume']
                vol_avg = last['vol_sma'] if not pd.isna(last['vol_sma']) else vol_current
                vol_status = "Forte" if vol_current > vol_avg * 1.5 else ("Fraco" if vol_current < vol_avg * 0.7 else "Medio")

                # SMC
                smc_data = analyze_smc(df)

                info = (
                    f"Timeframe: {tf} | Preco: {price:.4f} | VWAP: {vwap:.4f} ({vwap_pos}) | "
                    f"RSI: {rsi:.1f} | StochRSI K:{stoch_k:.1f} D:{stoch_d:.1f} ({stoch_status}) | "
                    f"Volume: {vol_status} | "
                    f"EMA9: {ema9:.4f} EMA21: {ema21:.4f} EMA200: {ema200:.4f} | "
                    f"Tendencia Curto Prazo: {trend_curto} | Tendencia Longo Prazo: {trend_longo} | "
                    f"MACD: {macd_val:.6f} Signal: {macd_sig:.6f} Histograma: {macd_hist:.6f}{macd_cross} | "
                    f"Bollinger: {bb_pos} | Largura BB: {bb_status} | "
                    f"ATR: {atr:.4f} ({atr_pct:.2f}% do preco) | "
                    f"Liquidez Alta: {smc_data['liquidity_high']:.4f} | Liquidez Baixa: {smc_data['liquidity_low']:.4f}"
                )

                if smc_data['fvg_bullish']:
                    info += f" | FVG Alta: {smc_data['fvg_bullish'][0]:.4f} - {smc_data['fvg_bullish'][1]:.4f}"
                if smc_data['fvg_bearish']:
                    info += f" | FVG Baixa: {smc_data['fvg_bearish'][0]:.4f} - {smc_data['fvg_bearish'][1]:.4f}"
                if smc_data['ob_bullish']:
                    info += f" | OB Alta: {smc_data['ob_bullish']:.4f}"
                if smc_data['ob_bearish']:
                    info += f" | OB Baixa: {smc_data['ob_bearish']:.4f}"
                if smc_data.get('swing_highs'):
                    info += f" | Estrutura de Topos: {smc_data['swing_highs']}"
                if smc_data.get('swing_lows'):
                    info += f" | Estrutura de Fundos: {smc_data['swing_lows']}"

                context_lines.append(info)
        except Exception as e:
            print(f"Erro no calculo de {symbol}: {e}")
            pass
            
    if context_lines:
        return "DADOS DO SISTEMA INSTITUCIONAL DE MERCADO PARA EMBASAR A ANALISE:\n" + "\n".join(context_lines)
    return ""

async def check_price_drops():
    top_coins = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT", "ADA/USDT"]
    alerts = []
    
    try:
        for symbol in top_coins:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1h", limit=2)
            if len(ohlcv) >= 2:
                old_price = ohlcv[0][1]
                current_price = ohlcv[-1][4]
                
                drop_pct = ((current_price - old_price) / old_price) * 100
                
                if drop_pct <= -2.0:
                    alerts.append(f"ALERTA URGENTE: {symbol} sofreu uma queda brusca de {drop_pct:.2f}% na ultima hora! Preco atual: {current_price:.4f}. Oportunidade de liquidez ou risco eminente.")
    except Exception as e:
        print(f"Erro ao checar drops: {e}")
        
    return alerts

def get_top_100_symbols():
    try:
        tickers = exchange.fetch_tickers()
        usdt_tickers = {k: v for k, v in tickers.items() if k.endswith('/USDT')}
        sorted_tickers = sorted(usdt_tickers.items(), key=lambda x: x[1].get('quoteVolume', 0) if x[1].get('quoteVolume') else 0, reverse=True)
        return [x[0] for x in sorted_tickers[:100]]
    except Exception as e:
        print(f"Erro ao buscar top 100: {e}")
        return ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]

def scan_for_opportunities_sync():
    print("[SISTEMA] Iniciando varredura matematica das Top 100...")
    top_symbols = get_top_100_symbols()
    opportunities = []
    
    for symbol in top_symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe="15m", limit=220)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df = calculate_indicators(df)

            smc_data = analyze_smc(df)
            last  = df.iloc[-1]
            prev  = df.iloc[-2]
            price = last['close']
            rsi   = last['RSI_14'] if not pd.isna(last['RSI_14']) else 50

            stoch_k = last['StochRSI_K'] if not pd.isna(last['StochRSI_K']) else 50
            macd_val = last['MACD']
            macd_sig = last['MACD_signal']
            bb_width = last['BB_width']
            atr      = last['ATR_14']
            vwap     = last['VWAP']
            ema9     = last['EMA_9']
            ema21    = last['EMA_21']
            ema200   = last['EMA_200']

            # --- Filtros de qualidade do setup ---
            is_oversold   = rsi < 35 and stoch_k < 25
            is_overbought = rsi > 65 and stoch_k > 75
            near_liq_low  = price <= smc_data['liquidity_low']  * 1.003
            near_liq_high = price >= smc_data['liquidity_high'] * 0.997
            macd_cross_up   = prev['MACD'] < prev['MACD_signal'] and macd_val > macd_sig
            macd_cross_down = prev['MACD'] > prev['MACD_signal'] and macd_val < macd_sig
            bb_squeeze      = bb_width < df['BB_width'].quantile(0.15)  # squeeze forte
            has_ob = smc_data['ob_bullish'] or smc_data['ob_bearish']

            if is_oversold or is_overbought or near_liq_low or near_liq_high or macd_cross_up or macd_cross_down or (bb_squeeze and has_ob):
                trend_curto = "ALTA" if ema9  > ema21  else "BAIXA"
                trend_longo = "ALTA" if price > ema200 else "BAIXA"
                vwap_pos    = "ACIMA do VWAP" if price > vwap else "ABAIXO do VWAP"
                atr_pct     = (atr / price) * 100
                macd_label  = ""
                if macd_cross_up:   macd_label = " [CRUZAMENTO ALTISTA]"
                if macd_cross_down: macd_label = " [CRUZAMENTO BAIXISTA]"
                bb_status = "SQUEEZE" if bb_squeeze else "NORMAL"

                context = (
                    f"ATIVO: {symbol.replace('/USDT', '')}\n"
                    f"Timeframe: 15m | Preco: {price:.4f} | VWAP: {vwap:.4f} ({vwap_pos})\n"
                    f"RSI: {rsi:.1f} | StochRSI K:{stoch_k:.1f} | "
                    f"MACD: {macd_val:.6f} vs Signal: {macd_sig:.6f}{macd_label}\n"
                    f"EMA9: {ema9:.4f} EMA21: {ema21:.4f} EMA200: {ema200:.4f} | "
                    f"Tendencia Curto: {trend_curto} | Tendencia Longo: {trend_longo}\n"
                    f"Bollinger: {bb_status} | ATR: {atr:.4f} ({atr_pct:.2f}%)\n"
                    f"Liquidez Alta: {smc_data['liquidity_high']:.4f} | Liquidez Baixa: {smc_data['liquidity_low']:.4f}"
                )
                if smc_data['fvg_bullish']:
                    context += f" | FVG Alta: {smc_data['fvg_bullish'][0]:.4f}-{smc_data['fvg_bullish'][1]:.4f}"
                if smc_data['fvg_bearish']:
                    context += f" | FVG Baixa: {smc_data['fvg_bearish'][0]:.4f}-{smc_data['fvg_bearish'][1]:.4f}"
                if smc_data['ob_bullish']:
                    context += f" | OB Alta: {smc_data['ob_bullish']:.4f}"
                if smc_data['ob_bearish']:
                    context += f" | OB Baixa: {smc_data['ob_bearish']:.4f}"

                opportunities.append(context)
        except Exception:
            pass
            
    return opportunities
