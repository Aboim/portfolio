import http.server
import subprocess
import os
import json
import socketserver

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(DIR), "push-all.ps1")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_POST(self):
        if self.path == "/push":
            try:
                result = subprocess.run(
                    ["pwsh", "-ExecutionPolicy", "Bypass", "-File", SCRIPT],
                    capture_output=True, text=True, timeout=120,
                    cwd=os.path.dirname(DIR)
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # silent

if __name__ == "__main__":
    print(f"\n  Portfolio em http://localhost:{PORT}\n")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor parado.")
