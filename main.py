import os, ccxt, time, threading, json
from flask import Flask
import numpy as np

app = Flask(__name__)

API_KEY = os.getenv("OKX_API_KEY")
SECRET = os.getenv("OKX_SECRET")
PASSWORD = os.getenv("OKX_PASSPHRASE")
symbol = "SOL/USDT"
STATE_FILE = "estado.json"

def cargar():
    try:
        with open(STATE_FILE,'r') as f: return json.load(f)
    except: return {"lowest": 99999, "highest": 0}

def guardar(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)

estado = cargar()

def get_ex():
    return ccxt.okx({'apiKey':API_KEY,'secret':SECRET,'password':PASSWORD,'enableRateLimit':True})

@app.route('/')
def home(): return f"VIVO - {estado}"

def bot():
    global estado
    hist=[]
    print(f"INICIADO CON MEMORIA: {estado}")
    while True:
        try:
            ex=get_ex()
            price=ex.fetch_ticker(symbol)['last']
            hist.append(price)
            if len(hist)>15: hist.pop(0)
            
            # RSI simple
            rsi=50
            if len(hist)>=14:
                d=np.diff(hist)
                g=np.mean([x for x in d if x>0]) or 0
                l=abs(np.mean([x for x in d if x<0])) or 0.0001
                rsi=100-(100/(1+g/l))

            bal=ex.fetch_balance()
            usdt=bal.get('USDT',{}).get('free',0)
            sol=bal.get('SOL',{}).get('free',0)

            print(f"Precio:{price:.2f} USDT:{usdt:.2f} SOL:{sol:.4f} | MEM L:{estado['lowest']:.2f} H:{estado['highest']:.2f} RSI:{rsi:.1f}")

            # 1. SI TIENE USDT -> ESTA EN MODO COMPRA, no importa que hacia antes
            if usdt > 1.1:
                if price < estado['lowest']:
                    estado['lowest']=price
                    guardar(estado)
                # Si subio 3% desde el fondo y RSI bajo -> COMPRA
                if estado['lowest']<99999 and price >= estado['lowest']*1.03 and rsi<50:
                    ex.create_market_buy_order(symbol, (usdt*0.6)/price)
                    print(f"*** COMPRA {estado['lowest']} -> {price}")
                    estado['highest']=price
                    estado['lowest']=99999
                    guardar(estado)

            # 2. SI TIENE SOL -> ESTA EN MODO VENTA
            if sol > 0.01:
                if price > estado['highest']:
                    estado['highest']=price
                    guardar(estado)
                # Si bajo 2.5% desde el techo y RSI alto -> VENDE
                if price <= estado['highest']*0.975 and rsi>50:
                    ex.create_market_sell_order(symbol, sol)
                    print(f"*** VENTA {estado['highest']} -> {price}")
                    estado['lowest']=price
                    estado['highest']=0
                    guardar(estado)

            time.sleep(10)
        except Exception as e:
            print(f"Error {e}")
            time.sleep(10)

threading.Thread(target=bot, daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
