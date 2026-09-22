import ccxt
import time
import requests
import os

SYMBOL = "SHIB/USDT"
PORC = 2.0

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
API_PASSPHRASE = os.getenv("API_PASSPHRASE")

PHONE = "5213121537009"
WAKEY = "4543250"

exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'password': API_PASSPHRASE,
    'enableRateLimit': True,
})

def wa(m):
    try:
        requests.get(f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={m}&apikey={WAKEY}", timeout=10)
    except:
        pass

bal = exchange.fetch_balance()
usdt = bal['total'].get('USDT', 0)
print(f"BOT SHIB 2% DINAMICO INICIADO con {usdt} USDT", flush=True)
wa(f"BOT SHIB 2% DINAMICO INICIADO con {usdt} USDT")

max_p = 0
min_p = 999999999.0

while True:
    try:
        price = exchange.fetch_ticker(SYMBOL)['last']
        b = exchange.fetch_balance()
        free_shib = b['free'].get('SHIB', 0)
        free_usdt = b['free'].get('USDT', 0)

        if free_shib > 100000:
            if price > max_p:
                max_p = price
            caida = ((max_p - price) / max_p * 100) if max_p > 0 else 0
            print(f"SHIB {price} MAX {max_p} caida {caida:.2f}%", flush=True)
            if caida >= PORC:
                exchange.create_market_sell_order(SYMBOL, free_shib * 0.99)
                wa(f"VENDI SHIB -{PORC}% a {price}")
                max_p = 0
                min_p = 999999999.0
        else:
            if price < min_p:
                min_p = price
            subida = ((price - min_p) / min_p * 100) if min_p != 999999999.0 else 0
            print(f"SHIB {price} MIN {min_p} subida {subida:.2f}%", flush=True)
            if subida >= PORC and free_usdt >= 1:
                amt = (free_usdt / price) * 0.99
                exchange.create_market_buy_order(SYMBOL, amt)
                wa(f"COMPRE SHIB +{PORC}% a {price}")
                max_p = 0
                min_p = 999999999.0

        time.sleep(10)
    except Exception as e:
        print(f"Error {e}", flush=True)
        time.sleep(10)
