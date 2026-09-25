import os
import time
import requests
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- FIX PARA RENDER - PUERTO DENTRO DEL PROGRAMA ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot B 3.5 WIF Sigo operando OK")

def iniciar_servidor():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Servidor dummy iniciado en puerto {port} para Render")
    server.serve_forever()

Thread(target=iniciar_servidor, daemon=True).start()
# --- FIN FIX ---

# --- CONFIGURACION ---
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
WHATSAPP_APIKEY = os.getenv("WHATSAPP_APIKEY")

SYMBOL = "WIFUSDT"
CAIDA_PARA_ACTIVAR = -2.5
REBOTE_COMPRA = 0.8
CAIDA_VENTA = -1.2
HEARTBEAT_MINUTOS = 30 # FIJO ADENTRO

BINANCE_URL = f"https://api.binance.com/api/v3/ticker/24hr?symbol={SYMBOL}"

ultimo_maximo = 0
en_espera_rebote = False
minimo_rebote = 0
precio_compra = 0
max_desde_compra = 0
en_posicion = False
ultimo_heartbeat = time.time()

def enviar_whatsapp(mensaje):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={mensaje}&apikey={WHATSAPP_APIKEY}"
        requests.get(url, timeout=15)
        print(f"WA: {mensaje}")
    except Exception as e:
        print(f"Error WA: {e}")

def obtener_precio():
    try:
        r = requests.get(BINANCE_URL, timeout=10)
        data = r.json()
        return float(data['lastPrice']), float(data['priceChangePercent'])
    except:
        return None, None

enviar_whatsapp(f"🚀 Bot B 3.5 CORREGIDO INICIADO - Con puerto fijo - {datetime.now().strftime('%H:%M')}")
print(f"Bot iniciado con heartbeat {HEARTBEAT_MINUTOS} min")

while True:
    try:
        precio, cambio_24h = obtener_precio()
        if precio is None:
            time.sleep(10)
            continue

        if not en_posicion:
            if ultimo_maximo == 0 or precio > ultimo_maximo:
                ultimo_maximo = precio
            caida_desde_max = ((precio - ultimo_maximo) / ultimo_maximo) * 100
            print(f"BUSCANDO | ${precio:.4f} | Caida: {caida_desde_max:.2f}%")

            if caida_desde_max <= CAIDA_PARA_ACTIVAR and not en_espera_rebote:
                en_espera_rebote = True
                minimo_rebote = precio

            if en_espera_rebote:
                if precio < minimo_rebote:
                    minimo_rebote = precio
                rebote = ((precio - minimo_rebote) / minimo_rebote) * 100
                if rebote >= REBOTE_COMPRA:
                    precio_compra = precio
                    max_desde_compra = precio
                    en_posicion = True
                    en_espera_rebote = False
                    ultimo_maximo = 0
                    enviar_whatsapp(f"🎯 COMPRA WIF\nMinimo: ${minimo_rebote:.4f}\nCompra: ${precio:.4f}\nRebote: +{rebote:.2f}%")
        else:
            if precio > max_desde_compra:
                max_desde_compra = precio
            caida_desde_max_pos = ((precio - max_desde_compra) / max_desde_compra) * 100
            ganancia_actual = ((precio - precio_compra) / precio_compra) * 100
            print(f"EN POSICION | ${precio:.4f} | Max ${max_desde_compra:.4f} | PnL {ganancia_actual:.2f}%")

            if caida_desde_max_pos <= CAIDA_VENTA and ganancia_actual > 0:
                enviar_whatsapp(f"💰 VENTA WIF\nCompra: ${precio_compra:.4f}\nMax: ${max_desde_compra:.4f}\nVenta: ${precio:.4f}\nGan: {ganancia_actual:.2f}%")
                en_posicion = False
                precio_compra = 0
                max_desde_compra = 0
                ultimo_maximo = precio

        if time.time() - ultimo_heartbeat > HEARTBEAT_MINUTOS * 60:
            estado = f"EN POSICION PnL {((precio - precio_compra)/precio_compra*100):.2f}%" if en_posicion else "BUSCANDO COMPRA"
            enviar_whatsapp(f"⚙️ Sigo operando - {estado} - WIF ${precio:.4f}")
            ultimo_heartbeat = time.time()

        time.sleep(20)
    except Exception as e:
        print(f"Error loop: {e}")
        time.sleep(20)
