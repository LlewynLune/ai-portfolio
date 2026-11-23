from __future__ import annotations
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from .config import Config
from .engine import compare

ROOT=Path(__file__).resolve().parents[1]
BUSY=threading.Lock()
MAX_BODY=8192

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def send(self,status,body,content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(body)))
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def json(self,status,payload):
        self.send(status,json.dumps(payload,ensure_ascii=False).encode())

    def valid_host(self):
        return self.headers.get("Host") in (f"127.0.0.1:{self.server.server_port}",f"localhost:{self.server.server_port}")

    def do_GET(self):
        if not self.valid_host():
            return self.json(403,{"error":"local host only"})
        if self.path == "/favicon.ico":
            return self.send(204,b"","image/x-icon")
        if self.path == "/health":
            return self.json(200,{"ok":True,"workload":"synthetic","llm_calls":0})
        if self.path in ("/","/index.html"):
            return self.send(200,(ROOT/"demo.html").read_bytes(),"text/html; charset=utf-8")
        return self.json(404,{"error":"not found"})

    def do_POST(self):
        if not self.valid_host():
            return self.json(403,{"error":"local host only"})
        expected=(f"http://127.0.0.1:{self.server.server_port}",f"http://localhost:{self.server.server_port}")
        if self.headers.get("Origin") not in expected:
            return self.json(403,{"error":"same-origin browser requests required"})
        if self.path != "/api/compare":
            return self.json(404,{"error":"not found"})
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return self.json(415,{"error":"JSON required"})
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0 < length <= MAX_BODY:
                return self.json(413,{"error":"body size out of bounds"})
            payload=json.loads(self.rfile.read(length))
            if not isinstance(payload,dict):
                raise ValueError("config must be an object")
            if payload.get("count",24)>48:
                raise ValueError("interactive count <= 48")
            cfg=Config(**payload)
        except (ValueError,TypeError,json.JSONDecodeError) as exc:
            return self.json(400,{"error":str(exc)})
        if not BUSY.acquire(blocking=False):
            return self.json(429,{"error":"one comparison at a time"})
        try:
            result=asyncio.run(compare(cfg))
            self.json(200,result)
        except (BrokenPipeError,ConnectionResetError):
            pass
        finally:
            BUSY.release()


def serve(port=8765):
    if not 1024 <= port <= 65535:
        raise ValueError("port must be 1024..65535")
    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    print(f"Open http://127.0.0.1:{port} — local synthetic demo, Ctrl+C to stop",flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
