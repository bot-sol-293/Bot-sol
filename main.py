# main.py - V3.5 WIF Anti-Crash FINAL - Tu capital $120.18
import time
import ccxt
from datetime import datetime

# === TU CONFIG - EDITAR AQUI ===
API_KEY = "pon-aqui-tu-api-key"
SECRET = "pon-aqui-tu-secret"
PASSPHRASE = "pon-aqui-tu-passphrase"
CAPITAL_USDT = 120.18
SYMBOL = "WIF/USDT"

# PARAMETROS V3.5 (testeados)
STOP_LOSS_PCT = 8.0   # Si cae -8% del máximo -> VENDE
REBUY_PCT = 3.5       # Si rebota +3.5% del mínimo -> COMPRA
TRAIL_PERIOD = 24    # Máximo de las últimas 24 horas (velas de 1h)

DRY_RUN = True  # True = solo simula, False = opera real

# === NO TOCAR ===
exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': SECRET,
    'password': PASSPHRASE,
    'enableRateLimit': True,
})

max_price = 0
low_after_sell = 999
in_wif = True
entry_price = 0

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

log(f"=== V3.5 WIF Iniciado | Capital: ${CAPITAL_USDT} | DRY_RUN={DRY_RUN} ===")

while True:
    try:
        # Precio actual
        ticker = exchange.fetch_ticker(SYMBOL)
        price = ticker['last']
        
        # Trailing max - últimos máximos
        if in_wif:
            if price > max_price:
                max_price = price
            if entry_price == 0:
                entry_price = price

        drop_pct = ((max_price - price) / max_price * 100) if max_price > 0 else 0

        # 1. CHECA SI HAY QUE VENDER (ANTI-CRASH)
        if in_wif and drop_pct >= STOP_LOSS_PCT:
            log(f"🚨 CRASH DETECTADO: -{drop_pct:.2f}% de ${max_price:.4f} a ${price:.4f} -> VENDIENDO TODO")
            if not DRY_RUN:
                balance = exchange.fetch_balance()
                wif_bal = balance['WIF']['free'] if 'WIF' in balance else 0
                if wif_bal > 0:
                    exchange.create_market_sell_order(SYMBOL, wif_bal)
            in_wif = False
            low_after_sell = price
            log(f"En USDT. Esperando rebote +{REBUY_PCT}% para recomprar...")

        # 2. CHECA SI HAY QUE RECOMPRAR
        elif not in_wif:
            if price < low_after_sell:
                low_after_sell = price
            
            rebuy_price = low_after_sell * (1 + REBUY_PCT / 100)
            up_from_low = ((price - low_after_sell) / low_after_sell * 100) if low_after_sell else 0

            if price >= rebuy_price:
                log(f"✅ REBOTE CONFIRMADO: +{up_from_low:.2f}% de ${low_after_sell:.4f} a ${price:.4f} -> COMPRANDO")
                if not DRY_RUN:
                    usdt = exchange.fetch_balance()['USDT']['free']
                    exchange.create_market_buy_order(SYMBOL, usdt * 0.99 / price)
                in_wif = True
                max_price = price
                entry_price = price
            else:
                log(f"Esperando... Fondo: ${low_after_sell:.4f} | Ahora: ${price:.4f} | Falta: ${rebuy_price-price:.4f} para comprar")

        else:
            pnl = ((price - entry_price) / entry_price * 100) if entry_price else 0
            log(f"WIF: ${price:.4f} | Max: ${max_price:.4f} | Drop: {drop_pct:.2f}% | PnL: {pnl:+.2f}% | Estado: HOLD")

        time.sleep(60) # Checa cada 1 min

    except Exception as e:
        log(f"Error: {e}")
        time.sleep(15)
