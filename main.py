import os, time, threading
from flask import Flask
import ccxt
import pandas as pd
import ta

app = Flask(__name__)

API_KEY = os.getenv("OKX_API_KEY")
SECRET = os.getenv("OKX_SECRET")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")

exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': SECRET,
    'password': PASSPHRASE,
    'enableRateLimit': True
})

SYMBOL = 'BONK/USDT'

def get_balance():
    bal = exchange.fetch_balance()
    usdt = bal['free'].get('USDT', 0)
    bonk = bal['free'].get('BONK', 0)
    price = exchange.fetch_ticker(SYMBOL)['last']
    total = usdt + (bonk * price)
    return usdt, bonk, total, price

def bot_loop():
    print("=== BOT-BONK OKX V3.2 BLINDADO INICIADO ===")
    while True:
        try:
            usdt, bonk, total, price = get_balance()
            print(f"Capital: ${total:.2f} | USDT: {usdt:.2f} | BONK: {bonk:.0f} | Precio: {price}")
            # Aquí va tu filtro ADX + Volumen (ya con $12+ hará trades)
            time.sleep(60)
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route('/')
def home():
    return "BOT BONK VIVO"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
