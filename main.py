import os
import time
import requests
from datetime import datetime

# --- CONFIGURACION ---
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
WHATSAPP_APIKEY = os.getenv("WHATSAPP_APIKEY")

SYMBOL = "WIFUSDT"
CAIDA_COMPRA = float(os.getenv("CAIDA_COMPRA", "-2.5"))
SUBIDA_VENTA = float(os.getenv("SUBIDA_VENTA", "1.8"))
HEARTBEAT_MINUTOS = 30 # FIJO ADENTRO, 30 MINUTOS

BINANCE_URL = f"https://api.binance.com/api/v3/ticker/24hr?symbol={SYMBOL}"

ultimo_precio = 0
precio_compra = 0
en_posicion = False
ultimo_heartbeat = 0

def enviar_whatsapp(mensaje):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={mensaje}&apikey={WHATSAPP_APIKEY}"
        r = requests.get(url, timeout=15)
        print(f"WhatsApp enviado: {mensaje} | Status: {r.status_code}")
    except Exception as e:
        print(f"Error enviando WhatsApp: {e}")

def obtener_precio_wif():
    try:
        r = requests.get(BINANCE_URL, timeout=10)
        data = r.json()
        precio = float(data['lastPrice'])
        cambio_24h = float(data['priceChangePercent'])
        return precio, cambio_24h
    except:
        return None, None

# --- INICIO ---
enviar_whatsapp(f"🚀 Bot B 3.5 WIF INICIADO - Cazando caida {CAIDA_COMPRA}% - {datetime.now().strftime('%H:%M:%S')}")
print(f"Bot B 3.5 Iniciado - Heartbeat cada {HEARTBEAT_MINUTOS} min")

ultimo_heartbeat = time.time()

while True:
    try:
        precio_actual, cambio_24h = obtener_precio_wif()
        if precio_actual is None:
            time.sleep(20)
            continue

        if not en_posicion:
            if ultimo_precio == 0:
                ultimo_precio = precio_actual
            if precio_actual > ultimo_precio:
                ultimo_precio = precio_actual
            
            caida_actual = ((precio_actual - ultimo_precio) / ultimo_precio) * 100
            print(f"Precio: ${precio_actual:.4f} | Caida: {caida_actual:.2f}% | 24h: {cambio_24h:.2f}%")

            if caida_actual <= CAIDA_COMPRA:
                precio_compra = precio_actual
                en_posicion = True
                mensaje = f"🎯 SUPER HIT COMPRA WIF\nPrecio: ${precio_actual:.4f}\nCaida: {caida_actual:.2f}%\n24h: {cambio_24h:.2f}%\nHora: {datetime.now().strftime('%H:%M:%S')}"
                enviar_whatsapp(mensaje)
                ultimo_precio = precio_actual
        else:
            subida = ((precio_actual - precio_compra) / precio_compra) * 100
            print(f"EN POSICION | Compra: ${precio_compra:.4f} | Actual: ${precio_actual:.4f} | PnL: {subida:.2f}%")

            if subida >= SUBIDA_VENTA:
                mensaje = f"💰 SUPER HIT VENTA WIF\nCompra: ${precio_compra:.4f}\nVenta: ${precio_actual:.4f}\nGanancia: {subida:.2f}%\nHora: {datetime.now().strftime('%H:%M:%S')}"
                enviar_whatsapp(mensaje)
                en_posicion = False
                ultimo_precio = precio_actual
                precio_compra = 0

        # --- HEARTBEAT CADA 30 MIN FIJO ---
        if time.time() - ultimo_heartbeat > HEARTBEAT_MINUTOS * 60:
            estado = "EN POSICION" if en_posicion else "BUSCANDO COMPRA"
            mensaje_heartbeat = f"⚙️ Sigo operando - {estado} - WIF ${precio_actual:.4f} - 24h {cambio_24h:.2f}% - Esperando caida {CAIDA_COMPRA}%"
            enviar_whatsapp(mensaje_heartbeat)
            ultimo_heartbeat = time.time()
            print("Heartbeat Sigo operando enviado")

        time.sleep(20)

    except Exception as e:
        print(f"Error en loop: {e}")
        time.sleep(20)
