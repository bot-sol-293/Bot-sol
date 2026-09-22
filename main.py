import os
import time
import requests
from okx import Trade, Market

API_KEY = os.getenv("OKX_API_KEY")
SECRET_KEY = os.getenv("OKX_SECRET_KEY")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")

PHONE = os.getenv("CALLMEBOT_PHONE", "5213121537009")
CALLMEBOT_KEY = os.getenv("CALLMEBOT_APIKEY", "4543250")

SYMBOL = "SOL-USDT"
TRAILING_PCT = 0.02 # 2% dinamico

trade = Trade.TradeAPI(API_KEY, SECRET_KEY, PASSPHRASE, False, "0")
market = Market.MarketAPI(API_KEY, SECRET_KEY, PASSPHRASE, False, "0")

max_price = 0
min_price = 999999

def whatsapp(msg):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={msg}&apikey={CALLMEBOT_KEY}"
        requests.get(url, timeout=10)
    except:
        pass

def get_price():
    ticker = market.get_ticker(SYMBOL)
    return float(ticker['data'][0]['last'])

def get_balance():
    bal = trade.get_account_balance()
    usdt = 0
    sol = 0
    for d in bal['data'][0]['details']:
        if d['ccy'] == 'USDT':
            usdt = float(d['availBal'])
        if d['ccy'] == 'SOL':
            sol = float(d['availBal'])
    return usdt, sol

print(f"🤖 Bot SOL Pro TRAILING {TRAILING_PCT*100}% INICIADO")

while True:
    try:
        price = get_price()
        usdt, sol = get_balance()

        if sol > 0.01:
            if price > max_price:
                max_price = price
                print(f"Nuevo MAXIMO: ${max_price:.4f}")
            if max_price > 0 and price <= max_price * (1 - TRAILING_PCT):
                print(f"🔻 VENDIENDO -2% desde ${max_price:.4f} en ${price:.4f}")
                whatsapp(f"🔻 SOL VENTA Trailing -2% desde ${max_price:.2f} -> ${price:.2f}")
                trade.place_order(instId=SYMBOL, tdMode="cash", side="sell", ordType="market", sz=str(sol))
                min_price = price
                max_price = 0
                time.sleep(10)
        else:
            if price < min_price:
                min_price = price
                print(f"Nuevo MINIMO: ${min_price:.4f}")
            if min_price < 999999 and price >= min_price * (1 + TRAILING_PCT):
                print(f"🔺 COMPRANDO +2% desde ${min_price:.4f} en ${price:.4f}")
                whatsapp(f"🔺 SOL COMPRA Trailing +2% desde ${min_price:.2f} -> ${price:.2f}")
                trade.place_order(instId=SYMBOL, tdMode="cash", side="buy", ordType="market", sz=str(usdt), ccyName="USDT")
                max_price = price
                min_price = 999999
                time.sleep(10)
        time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
