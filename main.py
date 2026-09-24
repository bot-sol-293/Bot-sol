import os, ccxt, time, threading, numpy as np
from flask import Flask

app = Flask(__name__)

API_KEY = os.getenv("OKX_API_KEY")
SECRET = os.getenv("OKX_SECRET")
PASSWORD = os.getenv("OKX_PASSPHRASE")

symbol = "SOL/USDT"
BUY_PCT = 0.03
SELL_PCT = 0.025

def get_exchange():
    return ccxt.okx({
        'apiKey': API_KEY,
        'secret': SECRET,
        'password': PASSWORD,
        'enableRateLimit': True
    })

@app.route('/')
def home():
    return "Bot SOL vivo - Cartera Real"

def bot_loop():
    lowest = 99999
    highest = 0
    history = []
    print("Bot SOL - MODO CARTERA REAL iniciado")
    while True:
        try:
            exchange = get_exchange()
            price = exchange.fetch_ticker(symbol)['last']
            history.append(price)
            if len(history) > 15: history.pop(0)
            
            rsi = 50
            if len(history) >= 14:
                diffs = np.diff(history)
                g = np.mean([d for d in diffs if d>0]) if any(d>0 for d in diffs) else 0
                l = abs(np.mean([d for d in diffs if d<0])) if any(d<0 for d in diffs) else 0.0001
                rsi = 100 - (100/(1+g/l)) if l!=0 else 50

            bal = exchange.fetch_balance()
            usdt = bal['USDT']['free'] if 'USDT' in bal else 0
            sol = bal['SOL']['free'] if 'SOL' in bal else 0

            if usdt > 1.1:
                if price < lowest: lowest = price
                if lowest < 99999 and price >= lowest*(1+BUY_PCT) and rsi < 50:
                    cant = (usdt*0.6)/price
                    exchange.create_market_buy_order(symbol, cant)
                    print(f"COMPRA {lowest:.2f}->{price:.2f}")
                    highest = price
                    lowest = 99999

            if sol > 0.01:
                if price > highest or highest==0: highest = price
                if price <= highest*(1-SELL_PCT) and rsi > 50:
                    exchange.create_market_sell_order(symbol, sol)
                    print(f"VENTA {highest:.2f}->{price:.2f}")
                    lowest = price
                    highest = 0
            
            print(f"OK {price:.2f} USDT:{usdt:.2f} SOL:{sol:.4f}")
            time.sleep(10)
        except Exception as e:
            print(f"Error en loop: {e}")
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
