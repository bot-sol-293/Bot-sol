import os
import time
import threading
import requests
from flask import Flask

# ============ 1. SERVIDOR PARA RENDER (para que no marque Timed Out) ============
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 B 3.5 Super Hits WIF - SPOT - Corriendo OK"

@app.route('/ping')
def ping():
    return "pong"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Iniciar web en segundo plano
threading.Thread(target=run_web, daemon=True).start()

# ============ 2. WHATSAPP ============
# Configura estas variables en Render > Environment
# WHATSAPP_PHONE = tu numero con +52 1...
# WHATSAPP_APIKEY = la que te da CallMeBot

def send_whatsapp(mensaje):
    try:
        phone = os.environ.get("WHATSAPP_PHONE") # ej: +523121234567
        apikey = os.environ.get("WHATSAPP_APIKEY") # ej: 1234567

        if not phone or not apikey:
            print(f"[WA] No hay credenciales, mensaje no enviado: {mensaje}")
            return

        # API de CallMeBot (gratis)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={requests.utils.quote(mensaje)}&apikey={apikey}"
        r = requests.get(url, timeout=15)
        print(f"[WA] Enviado: {r.text}")
    except Exception as e:
        print(f"[WA] Error enviando: {e}")

# ============ 3. BOT B 3.5 SUPER HITS WIF SPOT ============
# Si usas Bitget/Binance, pon tus keys en Render como variables

def get_wif_price():
    # Precio real de WIF con CoinGecko / Bitget publico (sin necesidad de key)
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=dogwifcoin&vs_currencies=usd", timeout=10).json()
        return float(r['dogwifcoin']['usd'])
    except:
        return 0

def bot_loop():
    print("🚀 Iniciando Bot B 3.5 Super Hits WIF - SPOT")
    send_whatsapp("🚀 Bot B 3.5 Super Hits INICIADO en Render. WIF SPOT listo.")

    balance_wif = 39 # tu balance inicial
    ultimo_precio = 0
    compras = 0

    time.sleep(5) # esperar a que Flask prenda

    while True:
        try:
            precio = get_wif_price()
            if precio == 0:
                time.sleep(10)
                continue

            print(f"[B 3.5] WIF: ${precio} | Balance: {balance_wif} WIF")

            # ====== AQUI TU ESTRATEGIA SUPER HITS ======
            # Ejemplo: Super Hits = si baja 3% del ultimo precio, compra
            # Tu puedes cambiar esta logica, es la que teniamos

            if ultimo_precio == 0:
                ultimo_precio = precio

            variacion = ((precio - ultimo_precio) / ultimo_precio) * 100

            # SUPER HIT: caída fuerte = oportunidad de compra SPOT (sin liquidacion)
            if variacion <= -2.5:
                msg = f"🎯 SUPER HIT DETECTADO WIF\nPrecio: ${precio}\nCaida: {variacion:.2f}%\nAccion: COMPRANDO SPOT\nBalance: {balance_wif}"
                print(msg)
                send_whatsapp(msg)
                # --- AQUI VA TU ORDEN REAL DE COMPRA ---
                # exchange.buy(WIF/USDT)
                ultimo_precio = precio
                compras += 1

            # SUPER HIT VENTA: subida fuerte
            elif variacion >= 3.0:
                msg = f"💰 SUPER HIT VENTA WIF\nPrecio: ${precio}\nSubida: +{variacion:.2f}%\nAccion: VENDIENDO SPOT\nGanancia estimada!"
                print(msg)
                send_whatsapp(msg)
                # --- AQUI VA TU ORDEN REAL DE VENTA ---
                ultimo_precio = precio

            time.sleep(20) # checa cada 20 segundos

        except Exception as e:
            print(f"[ERROR BOT] {e}")
            send_whatsapp(f"⚠️ Error en Bot B 3.5: {e}")
            time.sleep(30)

# ============ 4. KEEP ALIVE PARA QUE NO SE DUERMA (plan gratis) ============
def keep_alive():
    while True:
        time.sleep(540) # 9 min
        try:
            url = os.environ.get("RENDER_EXTERNAL_URL")
            if url:
                requests.get(url + "/ping", timeout=10)
                print("[KeepAlive] Ping OK")
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ============ ARRANQUE ============
if __name__ == "__main__":
    bot_loop()
