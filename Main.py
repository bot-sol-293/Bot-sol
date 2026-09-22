import os
import time
import threading
from flask import Flask
import okx.Account as Account
import okx.MarketData as MarketData
import okx.Trade as Trade

app = Flask(__name__)

API_KEY = os.getenv("OKX_API_KEY")
SECRET = os.getenv("OKX_SECRET")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")
SYMBOL = "SOL-USDT"

def get_price():
    try:
        market = MarketData.MarketAPI(flag="0")
        result = market.get_ticker(instId=SYMBOL)
        return float(result['data'][0]['last'])
    except Exception as e:
        print(f"Error precio: {e}")
        return None

def run_bot():
    print("Bot SOL iniciado...")
    while True:
        try:
            price = get_price()
            if price:
                print(f"Precio SOL: {price}")
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

@app.route('/')
def home():
    price = get_price()
    return f"Bot SOL Activo! Precio: {price}"

if __name__ == '__main__':
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
