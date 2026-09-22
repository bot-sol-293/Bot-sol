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
TRAILING = 0.02  # 2% dinamico

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot SOL Trailing 2% Activo"

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
    whatsapp("
