import os, time, threading
from flask import Flask
import ccxt

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

def bot_loop():
    print("=== BOT-BONK OKX V3.2 BLINDADO INICIADO ===", flush=True)
    while True:
        try:
            bal = exchange.fetch_balance()
            usdt = bal['free'].get('USDT', 0) or 0
            bonk = bal['free'].get('BONK', 0) or 0
            ticker = exchange.fetch_ticker(SYMBOL)
            price = ticker['last']
            total = usdt + (bonk * price)
            print(f"VIVO | Total: ${total:.2f} | USDT: {usdt:.2f} | BONK: {bonk:.0f} | Precio: {price}", flush=True)
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}", flush=True)
            time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route('/')
def home():
    return "BOT BONK V3.2 VIVO - BONK MODE"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
