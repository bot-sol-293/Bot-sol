import os, time, requests
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot B 3.5 Live")
    def log_message(self, *a):
        return

def run_server():
    port = int(os.getenv("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

Thread(target=run_server, daemon=True).start()

import datetime
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
WHATSAPP_APIKEY = os.getenv("WHATSAPP_APIKEY")
BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol=WIFUSDT"
CAIDA, REBOTE, CAIDA_V = -2.5, 0.8, -1.2

ult_max=0; espera=False; min_reb=0; p_compra=0; max_compra=0; en_pos=False; last_hb=time.time()

def wa(m):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={m}&apikey={WHATSAPP_APIKEY}", timeout=10)
    except: pass

def precio():
    try: return float(requests.get(BINANCE_URL, timeout=10).json()['lastPrice'])
    except: return None

wa(f"🚀 Bot B 3.5 INICIADO {datetime.datetime.now().strftime('%H:%M')}")

while True:
    try:
        p = precio()
        if not p: time.sleep(10); continue
        if not en_pos:
            if ult_max==0 or p>ult_max: ult_max=p
            caida = (p-ult_max)/ult_max*100 if ult_max else 0
            print(f"BUSCANDO ${p:.4f} caida {caida:.2f}%")
            if caida <= CAIDA and not espera: espera=True; min_reb=p
            if espera:
                if p<min_reb: min_reb=p
                reb = (p-min_reb)/min_reb*100 if min_reb else 0
                if reb >= REBOTE:
                    p_compra=p; max_compra=p; en_pos=True; espera=False; ult_max=0
                    wa(f"🎯 COMPRA WIF ${p:.4f} rebote {reb:.2f}%")
        else:
            if p>max_compra: max_compra=p
            caida_p = (p-max_compra)/max_compra*100 if max_compra else 0
            gan = (p-p_compra)/p_compra*100 if p_compra else 0
            print(f"EN POS ${p:.4f} max ${max_compra:.4f} PnL {gan:.2f}%")
            if caida_p <= -1.2 and gan>0:
                wa(f"💰 VENTA WIF ${p:.4f} Gan {gan:.2f}%")
                en_pos=False; p_compra=0; max_compra=0; ult_max=p; espera=False
        if time.time()-last_hb > 1800:
            wa(f"⚙️ Sigo operando - {'EN POS' if en_pos else 'BUSCANDO'} WIF ${p:.4f}")
            last_hb=time.time()
        time.sleep(20)
    except Exception as e:
        print(e); time.sleep(20)
