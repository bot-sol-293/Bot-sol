import os
import time
import threading
from flask import Flask
import okx.MarketData as MarketData

app = Flask(__name__)

def get_price():
    try:
        api = MarketData.MarketAPI(flag="0")
        res = api.get_ticker(instId="SOL-USDT")
        return float(res['data'][0]['last'])
    except:
        return None

def run_bot():
    while True:
        price = get_price()
        print(f"SOL Price: {price}")
        time.sleep(60)

@app.route('/')
def home():
    price = get_price()
    return f"Bot SOL 2.5% con $2.93 - OKX - Activo 24/7. Precio SOL: {price}"

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
