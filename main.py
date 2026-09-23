import ccxt, time, os, threading
import numpy as np
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot SOL $2.93 activo - 3%/2.5%"

# --- ENV VARS EN RENDER ---
API_KEY = os.getenv('OKX_API_KEY')
SECRET = os.getenv('OKX_SECRET')
PASSPHRASE = os.getenv('OKX_PASSPHRASE')

symbol = 'SOL/USDT'
BUY_PCT = 0.03
SELL_PCT = 0.025

exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': SECRET,
    'password': PASSPHRASE
})

lowest = 99999
highest = 0
in_position = False
history = []

def bot_loop():
    global lowest, highest, in_position, history
    print(f"Bot SOL $2.93 iniciado - {BUY_PCT*100}% / {SELL_PCT*100}% - RENDER")
    while True:
        try:
            price = exchange.fetch_ticker(symbol)['last']
            history.append(price)
            if len(history) > 15: history.pop(0)

            rsi = 50
            if len(history) >= 14:
                diffs = np.diff(history)
                g = np.mean([d for d in diffs if d>0]) if any(d>0 for d in diffs) else 0
                l = abs(np.mean([d for d in diffs if d<0])) if any(d<0 for d in diffs) else 0.0001
                rsi = 100 - (100/(1+g/l))

            bal = exchange.fetch_balance()
            usdt = bal['USDT']['free']
            sol = bal['SOL']['free']

            if not in_position:
                if price < lowest: lowest = price
                if lowest < 99999 and price >= lowest*(1+BUY_PCT) and rsi < 50:
                    amount_usdt = usdt * 0.6
                    if amount_usdt > 1:
                        exchange.create_market_buy_order(symbol, amount_usdt/price)
                        print(f"COMPRA fondo {lowest:.2f} -> {price:.2f} RSI {rsi:.1f}")
                        in_position = True
                        highest = price
                        lowest = 99999
            else:
                if price > highest: highest = price
                if price <= highest*(1-SELL_PCT) and rsi > 50:
                    if sol > 0.01:
                        exchange.create_market_sell_order(symbol, sol)
                        print(f"VENTA top {highest:.2f} -> {price:.2f} RSI {rsi:.1f}")
                        in_position = False
                        lowest = price
                        highest = 0
                if price <= highest*0.95 and highest != 0: # stop -5%
                    if sol > 0.01:
                        exchange.create_market_sell_order(symbol, sol)
                        print(f"STOP -5% en {price:.2f}")
                        in_position = False
                        lowest = price
                        highest = 0
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
