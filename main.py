from flask import Flask
import requests, os, threading, time
from datetime import datetime

app = Flask(__name__)

CAPITAL = 2.93
OBJETIVO = 2.5

def get_sol():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd", timeout=10).json()
        return r['solana']['usd']
    except:
        return 0

def loop():
    time.sleep(3)
    print("✅ Bot SOL 2.5% iniciado - $2.93")
    while True:
        price = get_sol()
        print(f"{datetime.now().strftime('%H:%M:%S')} SOL ${price} | Capital ${CAPITAL}")
        time.sleep(20)

threading.Thread(target=loop, daemon=True).start()

@app.route('/')
def home():
    price = get_sol()
    return f"<h1>Bot SOL OK - Live ✅</h1><p>SOL ${price} | Capital ${CAPITAL} | Objetivo {OBJETIVO}%</p>"

# ESTA ES LA LINEA QUE TE FALTABA PARA RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
