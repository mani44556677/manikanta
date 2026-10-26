"""Dependency-free demo API; not a production application server."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            status, body = 200, {"status": "ok"}
        elif self.path == "/":
            status, body = 200, {"service": "release-status", "version": os.getenv("APP_VERSION", "dev")}
        else:
            status, body = 404, {"error": "not found"}
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
