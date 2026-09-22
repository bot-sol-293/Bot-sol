import os
import ccxt
import time
from dotenv import load_dotenv

# 1. Cargar las credenciales seguras (Render las inyecta de forma automática)
load_dotenv()

# 2. Configurar la conexión con el exchange OKX
exchange = ccxt.okx({
    'apiKey': os.getenv('OKX_API_KEY'),
    'secret': os.getenv('OKX_SECRET_KEY'),
    'password': os.getenv('OKX_PASSPHRASE'),
    'enableRateLimit': True,  # Evita bloqueos por exceso de peticiones
})

# 3. Definir la criptomoneda a operar (Solana en mercado Spot contra USDT)
PAR_TRADING = 'SOL/USDT'

def verificar_conexion():
    """Comprueba que las API Keys configuradas en Render funcionen correctamente."""
    try:
        exchange.fetch_balance()
        print("✅ [OKX] ¡Conexión exitosa y segura!")
        return True
    except Exception as e:
        print("❌ [OKX] Error de autenticación. Revisa tus API keys en la pestaña Environment de Render.")
        print(f"Detalle del error: {e}")
        return False

def ejecutar_bot():
    """Bucle principal que monitorea el precio de Solana las 24 horas del día."""
    print(f"🤖 Bot iniciado con éxito. Monitoreando mercado de {PAR_TRADING} 24/7...")
    
    while True:
        try:
            # Obtener la información del mercado en tiempo real
            ticker = exchange.fetch_ticker(PAR_TRADING)
            precio_actual = ticker['last']
            
            print(f"🔄 [MERCADO] Precio actual de Solana (SOL): {precio_actual} USDT")
            
            # TODO: Aquí programaremos las condiciones matemáticas de compra y venta
            # Ejemplo: if precio_actual < precio_objetivo: comprar()
            
            # Esperar 60 segundos antes de realizar la siguiente consulta al mercado
            time.sleep(60)
            
        except Exception as e:
            print(f"⚠️ Ocurrió un error en el bucle de monitoreo: {e}")
            # Esperar 10 segundos antes de reintentar si falla la conexión de red temporalmente
            time.sleep(10)

if __name__ == "__main__":
    # Primero valida las llaves; si están correctas, el bot arranca a trabajar
    if verificar_conexion():
        ejecutar_bot()
