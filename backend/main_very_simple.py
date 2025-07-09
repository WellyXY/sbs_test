from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# Get port from environment variable or default to 8080
PORT = int(os.environ.get("PORT", 8080))

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Log every incoming request
        print(f"--- [SIMPLE SERVER] Received GET request for: {self.path} ---")
        
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')

def run():
    print(f"--- [SIMPLE SERVER] Starting http.server on port {PORT} ---")
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, SimpleServer)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    print(f"--- [SIMPLE SERVER] Server stopped. ---")

if __name__ == "__main__":
    run() 