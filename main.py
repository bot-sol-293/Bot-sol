import os
import time
import threading
import requests
from flask import Flask

# =========== CONFIG RENDER ===========
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 B 3.5 Super Hits WIF corriendo - Spot - Sin liquidacion"

@app.route('/ping')
def ping():
    return "pong"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Auto-ping para que no se duerma en Render gratis
def keep_alive():
    while True:
        time.sleep(540) # 9 minutos
        try:
            url = os.environ.get("RENDER_EXTERNAL_URL")
            if url:
                requests.get(url + "/ping", timeout=10)
                print("[KeepAlive] Ping enviado para no dormir")
        except Exception as e:
            print(f"[KeepAlive] Error: {e}")

# =========== TU BOT B 3.5 SUPER HITS ===========
# AQUI VA TU LOGICA REAL DE WIF
# Te dejo la estructura que ya teniamos

def bot_super_hits():
    print("🚀 Iniciando Bot B 3.5 Super Hits WIF - SPOT")
    print("Detectando balance...")

    # Esperar a que Flask inicie
    time.sleep(5)

    while True:
        try:
            # --- AQUI EMPIEZA TU ESTRATEGIA ---
            # Ejemplo: aqui va tu conexion a Bitget / Binance
            # y la logica de compra/venta de WIF

            print("[B 3.5] Checando precio WIF...")
            # tu codigo de trading...

            # Si no tienes el codigo a mano, pon aqui tu loop original

            time.sleep(10) # checa cada 10 segundos

        except Exception as e:
            print(f"[B 3.5] Error en bot: {e}")
            time.sleep(30)

# =========== ARRANQUE ===========
if __name__ == "__main__":
    # Hilo 1: Flask
    threading.Thread(target=run_flask, daemon=True).start()

    # Hilo 2: Keep Alive para que no se duerma
    threading.Thread(target=keep_alive, daemon=True).start()

    # Hilo 3: El Bot (principal)
    bot_super_hits()
