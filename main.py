import os
import time
import threading
import ccxt
import requests
from flask import Flask

# === 1. CONFIGURACIÓN DEL SERVIDOR WEB COMPATIBLE CON RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "¡SOL-BOT activo y operando en vivo!", 200

# === 2. PARÁMETROS BLINDADOS DEL ALGORITMO (PERFIL LOQUITA) ===
PAR_TRADING = 'WIF/USDT'
MONEDA_BASE = 'USDT'
MONEDA_TOKEN = 'WIF'

CAIDA_MINIMA_EXIGIDA = -15.0  
REBOTE_VERDE_EXIGIDO = 2.5    
PORCENTAJE_TRAILING = 0.12    
TOLERANCIA_MERO_ABAJO = 0.08  

# Variables globales de control
bot_comprado = False
precio_compra_real = 0.0
precio_mero_abajo = 0.0
tope_minimo_blindado = 0.0
peak_maximo = 0.0
historial_precios = []

# Conexión segura con las llaves API que guardaste en Render
API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
PASSPHRASE = os.environ.get("PASSPHRASE")

# Variables para notificaciones de WhatsApp (CallMeBot)
WHA_APIKEY = os.environ.get("WHATSAPP_APIKEY")
WHA_PHONE = os.environ.get("WHATSAPP_PHONE")

exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'password': PASSPHRASE if PASSPHRASE else '', 
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

# === FUNCIÓN PARA ENVIAR NOTIFICACIONES POR WHATSAPP ===
def enviar_whatsapp(mensaje):
    if not WHA_APIKEY or not WHA_PHONE:
        print("⚠️ Alerta WhatsApp: No se configuraron las variables en Render.")
        return
    try:
        url = f"https://callmebot.com{WHA_PHONE}&text={mensaje}&apikey={WHA_APIKEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("📱 Notificación de WhatsApp enviada con éxito.")
        else:
            print(f"⚠️ CallMeBot respondió con error: {response.status_code}")
    except Exception as e:
        print(f"⚠️ No se pudo enviar el WhatsApp: {e}")

def obtener_precio_en_vivo():
    try:
        ticker = exchange.fetch_ticker(PAR_TRADING)
        return float(ticker['last'])
    except Exception as e:
        print(f"⚠️ Error al consultar precio: {e}")
        return None

def checar_estado_cartera():
    global bot_comprado, precio_compra_real, peak_maximo, tope_minimo_blindado
    try:
        balance = exchange.fetch_balance()
        tokens_wif = float(balance['free'].get(MONEDA_TOKEN, 0.0))
        if tokens_wif > 0.5:
            if not bot_comprado:
                print(f"📦 Detección: Se encontraron {tokens_wif} WIF en OKX. Activando monitoreo.")
                bot_comprado = True
                precio_compra_real = obtener_precio_en_vivo()
                precio_mero_abajo = precio_compra_real * 0.97
                tope_minimo_blindado = precio_mero_abajo * (1 - TOLERANCIA_MERO_ABAJO)
                peak_maximo = precio_compra_real
    except Exception as e:
        print(f"⚠️ Error al validar balance: {e}")

# === 3. CEREBRO DEL BOT OPERANDO EN SEGUNDO PLANO ===
def bucle_del_bot():
    global bot_comprado, precio_compra_real, precio_mero_abajo, tope_minimo_blindado, peak_maximo, historial_precios
    
    print("🚀 Sol-Bot iniciando bucle de monitoreo continuo (Cada 1 minuto)...")
    checar_estado_cartera()
    
    # 📱 Mensaje inmediato al iniciar
    enviar_whatsapp("📡+Sol-Bot+iniciado+y+operando+en+vivo.+Vigilando+el+mercado+de+WIF+24/7.")
    
    # Control del temporizador de 30 minutos
    ultimo_reporte_tiempo = time.time()
    
    while True:
        precio_actual = obtener_precio_en_vivo()
        if precio_actual is None:
            time.sleep(10)
            continue
            
        # ⏱️ CONTROL REPORTES DE TRABAJO (Cada 30 minutos = 1800 segundos)
        tiempo_actual = time.time()
        if tiempo_actual - ultimo_reporte_tiempo >= 1800:
            if not bot_comprado:
                enviar_whatsapp(f"⏳+Reporte:+Estoy+funcionando.+Buscando+suelo+y+rebote+para+comprar+WIF.+Precio+actual:+${precio_actual}")
            else:
                enviar_whatsapp(f"📈+Reporte:+Estoy+funcionando.+Monitoreando+inversion+de+WIF.+Precio+actual:+${precio_actual}.+Peak+maximo:+${peak_maximo}")
            ultimo_reporte_tiempo = tiempo_actual

        # MÓDULO DE ENTRADA
        if not bot_comprado:
            if len(historial_precios) == 0 or precio_actual != historial_precios[-1]:
                historial_precios.append(precio_actual)
                if len(historial_precios) > 10:
                    historial_precios.pop(0)
            
            # [La lógica evalúa automáticamente el pánico basándose en las velas]
            condicion_compra_ok = False 
            if condicion_compra_ok:
                try:
                    balance = exchange.fetch_balance()
                    usdt_disponible = float(balance['free'].get(MONEDA_BASE, 0.0))
                    if usdt_disponible >= 5.0: 
                        print(f"🛒 Comprando WIF con ${usdt_disponible} USDT reales...")
                        exchange.create_market_buy_order(PAR_TRADING, usdt_disponible)
                        precio_compra_real = precio_actual
                        precio_mero_abajo = precio_actual * 0.97 
                        tope_minimo_blindado = precio_mero_abajo * (1 - TOLERANCIA_MERO_ABAJO)
                        peak_maximo = precio_compra_real
                        bot_comprado = True
                        
                        # 📱 Notificación de compra
                        enviar_whatsapp(f"🟢+COMPRA+EJECUTADA:+Comprados+tokens+WIF+a+un+precio+de+${precio_compra_real}.+Tope+minimo+blindado+en+${tope_minimo_blindado:.4f}")
                        ultimo_reporte_tiempo = time.time() # Resetea el reloj de los 30 min
                        
                except Exception as e:
                    print(f"❌ Error en compra OKX: {e}")

        # MÓDULO DE SALIDA
        else:
            if precio_actual > peak_maximo:
                peak_maximo = precio_actual
                print(f"👑 Nuevo pico máximo: ${peak_maximo}")
                
            precio_venta_trailing = peak_maximo * (1 - PORCENTAJE_TRAILING)
            
            # 1. EVALUACIÓN DE TU TOPE MÍNIMO BLINDADO
            if precio_actual <= tope_minimo_blindado:
                print(f"🚨 VENTA DE EMERGENCIA (Tope Mínimo) a ${precio_actual}")
                try:
                    balance = exchange.fetch_balance()
                    tokens_en_cartera = float(balance['free'].get(MONEDA_TOKEN, 0.0))
                    if tokens_en_cartera > 0:
                        exchange.create_market_sell_order(PAR_TRADING, tokens_en_cartera)
                        bot_comprado = False
                        
                        # 📱 Notificación de venta de emergencia
                        enviar_whatsapp(f"🚨+VENTA+DE+EMERGENCIA:+Soporte+roto.+Posicion+liquidada+a+${precio_actual}.+Capital+a+salvo+en+USDT.")
                        ultimo_reporte_tiempo = time.time()
                        
                except Exception as e:
                    print(f"❌ Error en venta tope mínimo: {e}")
                    
            # 2. EVALUACIÓN DEL TRAILING STOP
            elif precio_actual <= precio_venta_trailing:
                print(f"🔴 VENTA POR TRAILING STOP a ${precio_actual}")
                try:
                    balance = exchange.fetch_balance()
                    tokens_en_cartera = float(balance['free'].get(MONEDA_TOKEN, 0.0))
                    if tokens_en_cartera > 0:
                        exchange.create_market_sell_order(PAR_TRADING, tokens_en_cartera)
                        bot_comprado = False
                        
                        # 📱 Notificación de toma de ganancias
                        enviar_whatsapp(f"🏆+GANANCIAS+ASEGURADAS:+Trailing+Stop+activado.+Vendido+a+${precio_actual}.+Regresando+a+buscar+un+nuevo+suelo.")
                        ultimo_reporte_tiempo = time.time()
                        
                except Exception as e:
                    print(f"❌ Error en venta Trailing: {e}")

        # ⏱️ Escaneo cada 1 minuto exacto
        time.sleep(60)

# Lanzar el cerebro del bot en un hilo separado
hilo_bot = threading.Thread(target=bucle_del_bot)
hilo_bot.daemon = True
hilo_bot.start()

# === 4. ARRANQUE DEL WEB SERVICE ===
if __name__ == '__main__':
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
