#!/usr/bin/env python3
"""Serve a build and accept screenshots back from it.

The extension can take a screenshot but cannot write one to disk. A page served from
here can: it renders itself with html2canvas and POSTs the PNG to /_shot/<name>.png,
which lands in --shots. Same origin, so no download prompt and no per-file limit.
"""
import argparse, os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class H(SimpleHTTPRequestHandler):
    def do_POST(self):
        if not self.path.startswith('/_shot/'):
            self.send_error(404); return
        name = os.path.basename(self.path[len('/_shot/'):]) or 'shot.png'
        if not name.endswith('.png'): name += '.png'
        n = int(self.headers.get('Content-Length', 0))
        if n <= 0 or n > 20_000_000:
            self.send_error(413); return
        path = os.path.join(self.server.shots, name)
        with open(path, 'wb') as f:
            f.write(self.rfile.read(n))
        self.send_response(200); self.send_header('Content-Type','text/plain')
        self.send_header('Access-Control-Allow-Origin','*'); self.end_headers()
        self.wfile.write(path.encode())
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Headers','*'); self.end_headers()
    def log_message(self, *a): pass

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.'); ap.add_argument('--shots', default='./shots')
    ap.add_argument('--port', type=int, default=8903)
    a = ap.parse_args()
    os.makedirs(a.shots, exist_ok=True); os.chdir(a.root)
    srv = ThreadingHTTPServer(('127.0.0.1', a.port), H)
    srv.shots = os.path.abspath(a.shots)
    print(f"serving {os.path.abspath(a.root)} on {a.port}, shots to {srv.shots}", flush=True)
    srv.serve_forever()
