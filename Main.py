import os
import ccxt
import time
from dotenv import load_dotenv

# 1. Cargar las credenciales (sirve por si lo pruebas en compu, en Render se cargan solas)
load_dotenv()

# 2. Configurar la conexión segura con OKX usando las variables de entorno
exchange = ccxt.okx({
    'apiKey': os.getenv('OKX_API_KEY'),
    'secret': os.getenv('OKX_SECRET_KEY'),
    'password': os.getenv('OKX_PASSPHRASE'),
    'enableRateLimit': True,  # Evita que OKX bloquee tu servidor por exceso de peticiones
})

def verificar_conexion():
    """Comprueba que tus API Keys tengan permisos correctos."""
    try:
        balance = exchange.fetch_balance()
        print("✅ [OKX] ¡Conexión exitosa y segura!")
        return True
    except Exception as e:
        print("❌ [OKX] Error de autenticación. Revisa las variables en Render.")
        print(f"Detalle del error: {e}")
        return False

def ejecutar_bot():
    """Aquí irá la lógica de tu estrategia de Solana (SOL) más adelante."""
    print("🤖 Bot iniciado. Monitoreando mercado de Solana 24/7...")
    
    # Bucle infinito para que corra todo el tiempo en tu servidor
    while True:
        try:
            # Aquí es donde el bot consultará precios y tomará decisiones
            print("🔄 Revisando mercado...")
            
            # Espera 60 segundos antes de volver a revisar (puedes cambiar este tiempo después)
            time.sleep(60) 
            
        except Exception as e:
            print(f"⚠️ Ocurrió un error en el bucle: {e}")
            time.sleep(10) # Espera un poco antes de reintentar si falla el internet

if __name__ == "__main__":
    # Primero verifica las llaves; si están bien, arranca el bot 24/7
    if verificar_conexion():
        ejecutar_bot()
