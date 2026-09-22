import os, time, threading, requests, ccxt
from flask import Flask
app = Flask(__name__)

SYMBOL = 'SOL/USDT'
OBJ = 0.025  # 2.5% para activar la logica

# Estado para ver en la web
estado = {"actual":0,"compra":0,"maximo":0,"minimo":9999,"bajadas":0,"subidas":0,"msg":"Iniciando"}

# TUS DATOS DE WHATSAPP YA PUESTOS
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "5213121537009")
WHATSAPP_APIKEY = os.getenv("WHATSAPP_APIKEY", "4543250")

def send_whatsapp(mensaje):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={requests.utils.quote(mensaje)}&apikey={WHATSAPP_APIKEY}"
        requests.get(url, timeout=10)
        print(f"WhatsApp enviado: {mensaje}")
    except Exception as e:
        print(f"Error WhatsApp: {e}")

def get_price():
    try:
        return float(requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd", timeout=10).json()['solana']['usd'])
    except:
        return estado["actual"] or 116

def bot():
    ex = ccxt.okx({
        'apiKey': os.getenv("OKX_API_KEY"),
        'secret': os.getenv("OKX_SECRET"),
        'password': os.getenv("OKX_PASSPHRASE"),
        'enableRateLimit': True
    })
    print("BOT PRO FINAL - 2 subidas / 2 bajadas + WhatsApp")
    send_whatsapp("🤖 Bot SOL Pro INICIADO con $2.93 | Compra: 2 subidas tras caer -2.5% | Venta: 2 bajadas tras subir +2.5%")
    
    prev = 0
    ref_caida = 0

    while True:
        try:
            try:
                p = float(ex.fetch_ticker(SYMBOL)['last'])
            except:
                p = get_price()
            estado["actual"] = p

            bal = ex.fetch_balance()
            usdt_free = float(bal['USDT']['free']) if 'USDT' in bal else 0
            sol_free = float(bal['SOL']['free']) if 'SOL' in bal else 0

            # Contar rachas de subida/bajada
            if prev > 0:
                if p > prev:
                    estado["subidas"] += 1
                    estado["bajadas"] = 0
                elif p < prev:
                    estado["bajadas"] += 1
                    estado["subidas"] = 0

            # === SI NO TENEMOS SOL -> LOGICA DE COMPRA ===
            # Espera caida de -2.5% y luego 2 subidas seguidas para comprar
            if sol_free < 0.01:
                if ref_caida == 0:
                    ref_caida = p
                    estado["minimo"] = p
                if p < estado["minimo"]:
                    estado["minimo"] = p
                
                caida = (p - ref_caida) / ref_caida if ref_caida else 0

                if caida <= -OBJ and estado["subidas"] >= 2:
                    if usdt_free >= 1:
                        cant = round((usdt_free/p)*0.99, 3)
                        if cant >= 0.01:
                            ex.create_market_buy_order(SYMBOL, cant)
                            estado["compra"] = p
                            estado["maximo"] = p
                            msg = f"🟢 COMPRE {cant} SOL a ${p:.2f} | Caida {caida*100:.2f}% + rebote {estado['subidas']} subidas | Min ${estado['minimo']:.2f}"
                            estado["msg"] = msg
                            send_whatsapp(msg)
                            ref_caida = 0
                            estado["subidas"]=0
                            estado["bajadas"]=0
                else:
                    estado["msg"] = f"Esperando compra | Caida {caida*100:.2f}% | Subidas {estado['subidas']}/2 | Min ${estado['minimo']:.2f}"

            # === SI TENEMOS SOL -> LOGICA DE VENTA ===
            # Espera subida de +2.5% y luego 2 bajadas seguidas para vender
            else:
                if estado["compra"] == 0:
                    estado["compra"] = p
                    estado["maximo"] = p
                if p > estado["maximo"]:
                    estado["maximo"] = p
                
                gan = (p - estado["compra"]) / estado["compra"] if estado["compra"] else 0

                if gan >= OBJ and estado["bajadas"] >= 2:
                    ex.create_market_sell_order(SYMBOL, sol_free)
                    profit = (p - estado["compra"]) * sol_free
                    msg = f"🔴 VENDI +{gan*100:.2f}% a ${p:.2f} | Max ${estado['maximo']:.2f} | Ganancia ${profit:.2f} con 2 bajadas confirmadas"
                    estado["msg"] = msg
                    send_whatsapp(msg)
                    estado["compra"]=0
                    estado["maximo"]=0
                    ref_caida = p
                    estado["minimo"]=p
                    estado["bajadas"]=0
                else:
                    if gan >= OBJ:
                        estado["msg"] = f"TRAILING +{gan*100:.2f}% Max ${estado['maximo']:.2f} Bajadas {estado['bajadas']}/2 esperando 2 bajadas"
                    else:
                        estado["msg"] = f"HOLD +{gan*100:.2f}% esperando +2.5% | Max ${estado['maximo']:.2f}"

            prev = p
            print(f"SOL ${p} | {estado['msg']}")
        except Exception as e:
            print(f"Error: {e}")
            estado["msg"] = f"Error: {e}"
        time.sleep(20)

threading.Thread(target=bot, daemon=True).start()

@app.route("/")
def home():
    return f"<h1>Bot SOL Pro ✅ 2x2 + WhatsApp</h1><p>Precio actual: ${estado['actual']}</p><p>{estado['msg']}</p>"

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
