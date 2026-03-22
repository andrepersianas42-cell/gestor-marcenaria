import http.server
import socketserver
import socket
import os

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

print(f"\n--- GESTOR MARCENARIA - COMPARTILHAR APK ---\n")
print(f"1. Certifique-se que o APK está na pasta 'bin'.")
print(f"2. Conecte seu celular no mesmo Wi-Fi deste PC.")
print(f"3. Acesse este endereço no navegador do seu celular/tablet:\n")
print(f"   >>> http://{get_ip()}:{PORT}/bin/ <<<\n")
print(f"4. Toque no arquivo .apk para baixar e instalar.\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor rodando porta {PORT}... Pressione CTRL+C para parar.")
    httpd.serve_forever()
