import os
import time
import requests
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- FIX PARA RENDER WEB SERVICE - PUERTO DENTRO DEL PROGRAMA ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot B 3.5 WIF Sigo operando OK")

def iniciar_servidor():
    port = int(os.getenv("PORT", "10000"))
    server = HTTP
