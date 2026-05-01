import http.server
import socketserver
import base64
from datetime import datetime

PORT = 5000

class Listener(http.server.SimpleHTTPRequestHandler):
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if "/log" in self.path:
            # forged a response with plain text (avoid CORS error)
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            try:
                query = self.path.split("data=")[1]
                decoded_data = base64.b64decode(query).decode('utf-8')
                print(f"\n[{datetime.now()}] SUCCESS:")
                print(f"{decoded_data}")

                with open("output_data.txt", "a") as f:
                    f.write(f"{datetime.now()} - {decoded_data}\n")
            except Exception as e:
                print(f"Error decoding data: {e}")

            self.wfile.write(b"OK")
        else:
            super().do_GET()

print(f"[LOG] Server is running on {PORT}...")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Listener) as httpd:
    httpd.serve_forever()