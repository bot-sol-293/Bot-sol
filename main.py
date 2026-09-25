# main.py - BOT-BONK V3.1 BLINDADO - VIVO
import os, time, threading
import pandas as pd
import ta, ccxt
from flask import Flask

SYMBOL = "BONK/USDT"
TIMEFRAME = "15m"
RIESGO = 0.03

app = Flask(__name__)
@app.route('/')
def home():
    return "BOT-BONK V3.1 VIVO"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

def get_exchange():
    return ccxt.binance({
        'apiKey': os.getenv("API_KEY"),
        'secret': os.getenv("API_SECRET"),
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })

def get_capital(ex):
    b = ex.fetch_balance()
    return float(b['total'].get('USDT', 0) or b['free'].get('USDT', 0))

def get_df(ex):
    ohlcv = ex.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=100)
    return pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])

def filtro_tendencia(df):
    adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], 14).adx().iloc[-1]
    return adx > 20

def filtro_volumen(df):
    vol_avg = df['volume'].rolling(20).mean().iloc[-1]
    return df['volume'].iloc[-1] > vol_avg * 1.5

def senal(df):
    ema9 = ta.trend.EMAIndicator(df['close'], 9).ema_indicator().iloc[-1]
    ema21 = ta.trend.EMAIndicator(df['close'], 21).ema_indicator().iloc[-1]
    rsi = ta.momentum.RSIIndicator(df['close'], 14).rsi().iloc[-1]
    if not filtro_tendencia(df): return None
    if not filtro_volumen(df): return None
    if ema9 > ema21 and 55 < rsi < 72: return "LONG"
    if ema9 < ema21 and 28 < rsi < 45: return "SHORT"
    return None

def trade(ex, tipo, capital):
    monto = capital * RIESGO
    if monto < 5: 
        print(f"Capital bajo ${capital}")
        return
    precio = ex.fetch_ticker(SYMBOL)['last']
    cant = monto / precio
    print(f"{tipo} | ${capital:.2f} -> {cant:.0f} BONK @ {precio}")
    if tipo == "LONG":
        ex.create_market_buy_order(SYMBOL, cant)
    else:
        bal = ex.fetch_balance()['free'].get('BONK', 0)
        if bal > 0: ex.create_market_sell_order(SYMBOL, bal)

def bot_loop():
    ex = get_exchange()
    print("=== BOT-BONK V3.1 VIVO INICIADO ===")
    while True:
        try:
            cap = get_capital(ex)
            df = get_df(ex)
            s = senal(df)
            print(f"Capital ${cap:.2f} | Señal {s}")
            if s: trade(ex, s, cap)
            time.sleep(60)
        except Exception as e:
            print(f"Error {e}")
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    run_flask()
