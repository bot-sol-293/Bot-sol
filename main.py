import os
import time
import ccxt
import requests
from threading import Thread
from flask import Flask

API_KEY = os.getenv("OKX_API_KEY")
SECRET = os.getenv("OKX_SECRET_KEY")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")
CALLMEBOT_KEY = os.getenv("CALLMEBOT_APIKEY")

PHONE = "5213121537009"
SYMBOL = "SOL/USDT"
TRAILING = 0.02

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot SOL 2% Activo"

exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': SECRET,
    'password': PASSPHRASE,
})

def whatsapp(msg):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={msg}&apikey={CALLMEBOT_KEY}"
        requests.get(url, timeout=10)
    except:
        pass

def bot_logic():
    max_price = 0
    min_price = 9999999
    print("BOT SOL 2% DINAMICO INICIADO")
    whatsapp("Bot SOL 2% DINAMICO iniciado en Render")

    while True:
        try:
            price = exchange.fetch_ticker(SYMBOL)['last']
            balance = exchange.fetch_balance()
            usdt = balance['free'].get('USDT', 0)
            sol = balance['free'].get('SOL', 0)

            if sol > 0.01:
                if price > max_price:
                    max_price = price
                    print(f"Nuevo MAX {max_price}")
                if max_price > 0 and price <= max_price * (1 - TRAILING):
                    whatsapp(f"VENDIENDO SOL -2% desde max {max_price:.2f} a {price:.2f}")
                    exchange.create_market_sell_order(SYMBOL, sol)
                    min_price = price
                    max_price = 0
                    time.sleep(10)
            else:
                if price < min_price:
                    min_price = price
                    print(f"Nuevo MIN {min_price}")
                if min_price < 999999 and price >= min_price * (1 + TRAILING):
                    whatsapp(f"COMPRANDO SOL +2% desde min {min_price:.2f} a {price:.2f}")
                    if usdt > 5:
                        exchange.create_market_buy_order(SYMBOL, usdt)
                    max_price = price
                    min_price = 9999999
                    time.sleep(10)
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
    bot_logic()
