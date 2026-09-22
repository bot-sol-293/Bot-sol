import os
import ccxt
import time
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno (Render las inyecta automáticamente)
load_dotenv()

# Configuración del par y porcentajes
SYMBOL = "SHIB/USDT"
PORC = 3.5          # Margen de confirmación para comprar tras el suelo y trailing para vender
STOP_LOSS = 3.0     # Red de seguridad: Máxima pérdida permitida desde el precio de compra
TIMEFRAME = '1m'

# Tasa de comisión de OKX para cuentas estándar (0.1% = 0.001)
OKX_FEE = 0.001

# Archivo local (Nota: Render lo borra si el servidor se reinicia, el código ya maneja esto)
PRECIO_COMPRA_FILE = "precio_compra.txt"

# CORRECCIÓN: Nombres alineados con las variables que guardaste en Render
API_KEY = os.getenv("OKX_API_KEY")
API_SECRET = os.getenv("OKX_SECRET_KEY")
API_PASSPHRASE = os.getenv("OKX_PASSPHRASE")

# Formato de teléfono para México y API de CallMeBot
PHONE = "+523121537009"
WAKEY = "4543250"

# Inicialización segura del exchange OKX
exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'password': API_PASSPHRASE,
    'enableRateLimit': True,
})

def wa(m):
    """Envía notificaciones de WhatsApp usando la API oficial de CallMeBot."""
    try:
        # CORRECCIÓN: Estructura exacta y segura de la URL de CallMeBot
        url = f"https://callmebot.com{PHONE}&text={requests.utils.quote(m)}&apikey={WAKEY}"
        requests.get(url, timeout=5)
    except Exception as e:
        print(f"Error enviando mensaje de WhatsApp: {e}", flush=True)

def obtener_precio_vela():
    """Obtiene el último precio de cierre confirmado de la vela actual."""
    try:
        ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=2)
        if ohlcv and len(ohlcv) > 0:
            return float(ohlcv[-1][4]) # Índice 4 es el precio de cierre 'close'
    except Exception as e:
        print(f"Error al obtener velas de OKX: {e}", flush=True)
    return None

def guardar_precio_compra(precio):
    try:
        with open(PRECIO_COMPRA_FILE, "w") as f:
            f.write(str(precio))
    except Exception as e:
        print(f"Error al escribir archivo local: {e}", flush=True)

def leer_precio_compra():
    if os.path.exists(PRECIO_COMPRA_FILE):
        with open(PRECIO_COMPRA_FILE, "r") as f:
            try: 
                return float(f.read().strip())
            except: 
                return 0.0
    return 0.0

# Inicio del sistema y prueba de llaves
try:
    bal = exchange.fetch_balance()
    usdt = bal['total'].get('USDT', 0)
    print(f"BOT SHIB CON PROTECCION INICIADO con {usdt} USDT", flush=True)
    wa(f"🤖 BOT SHIB INICIADO con {usdt} USDT")
except Exception as e:
    print(f"❌ Error crítico de inicio: Revisa tus credenciales en Render. Detalle: {e}", flush=True)
    time.sleep(60)
    exit(1)

max_p = 0.0
min_p = 999999999.0
precio_entrada = leer_precio_compra()

while True:
    try:
        price = obtener_precio_vela()
        if price is None:
            time.sleep(15)
            continue

        b = exchange.fetch_balance()
        free_shib = b['free'].get('SHIB', 0)
        free_usdt = b['free'].get('USDT', 0)

        # LÁGICA DE VENTA (Cuando tienes SHIB acumulado)
        if free_shib > 100000:
            if precio_entrada == 0.0:
                precio_entrada = price
                guardar_precio_compra(precio_entrada)

            if price > max_p:
                max_p = price
            
            # Calcular variaciones porcentuales reales
            perdida_real = ((precio_entrada - price) / precio_entrada * 100) if precio_entrada > 0 else 0
            caida_desde_max = ((max_p - price) / max_p * 100) if max_p > 0 else 0
            
            print(f"[MODO VENTA] SHIB: {price:.8f} | Entrada con Fee: {precio_entrada:.8f} (-{perdida_real:.2f}%) | MAX: {max_p:.8f} (Trailing: -{caida_desde_max:.2f}%)", flush=True)
            
            # ACCIÓN: Venta por Stop Loss o Trailing Profit
            if perdida_real >= STOP_LOSS or caida_desde_max >= PORC:
                exchange.create_market_sell_order(SYMBOL, free_shib * 0.995)
                precio_salida_real = price * (1 - OKX_FEE)
                
                if perdida_real >= STOP_LOSS:
                    wa(f"🛑 STOP LOSS ACTIVADO. Vendí SHIB a aprox {precio_salida_real:.8f} (-{STOP_LOSS}% alcanzado).")
                else:
                    wa(f"📈 TRAILING PROFIT ACTIVADO. Vendí SHIB a aprox {precio_salida_real:.8f} tras caer {PORC}% desde el máximo.")
                
                max_p = 0.0
                min_p = 999999999.0
                precio_entrada = 0.0
                guardar_precio_compra(0.0)

        # LÓGICA DE COMPRA (Cuando tienes el saldo líquido en USDT)
        else:
            if price < min_p:
                min_p = price
            
            subida = ((price - min_p) / min_p * 100) if min_p != 999999999.0 else 0
            print(f"[MODO COMPRA] SHIB: {price:.8f} | MÍNIMO LOCAL: {min_p:.8f} | Subida actual: {subida:.2f}% | Disp: {free_usdt:.2f} USDT", flush=True)
            
            # Ejecuta la compra si sube el % configurado y tienes al menos $2 USDT libres
            if subida >= PORC and free_usdt >= 2.0:
                amt = (free_usdt / price) * 0.992
                exchange.create_market_buy_order(SYMBOL, amt)
                
                precio_entrada = price * (1 + OKX_FEE)
                guardar_precio_compra(precio_entrada)
                
                wa(f"🛒 COMPRA EJECUTADA EN SHIB. Precio mercado: {price:.8f}. Precio equilibrio ajustado con Fee: {precio_entrada:.8f}.")
                max_p = price
                min_p = 999999999.0

        time.sleep(15)

    except Exception as e:
        print(f"Error general en el bucle: {e}", flush=True)
        time.sleep(15)
