#!/usr/bin/env python3
"""Wake-on-visit front for the dashboard.

launchd holds TCP :8501 and starts this script only when someone opens the
address (the listening socket arrives as LISTEN_FDS). Plain HTTP is answered
here; Streamlit starts on an internal port at first use, and WebSocket
upgrades are spliced straight through so the app stays live. At login no
process runs - the kernel just holds the doorbell socket.
"""

from __future__ import annotations

import os
import select
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACK_PORT = int(os.environ.get("DASHBOARD_INTERNAL_PORT", "8502"))
BACK_HOST = "127.0.0.1"
BACK_URL = f"http://{BACK_HOST}:{BACK_PORT}"
LOG_DIR = Path.home() / "Library" / "Logs" / "personal-dashboard"
LOG_FILE = LOG_DIR / "serve.log"
STREAMLIT = ROOT / ".venv" / "bin" / "streamlit"

_lock = threading.Lock()


def log(message: str) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{stamp} {message}\n")
    except OSError:
        pass


def backend_healthy() -> bool:
    try:
        with urllib.request.urlopen(f"{BACK_URL}/_stcore/health", timeout=2) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def ensure_backend() -> None:
    with _lock:
        if backend_healthy():
            return
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_handle = open(LOG_FILE, "a", encoding="utf-8")
        subprocess.Popen(
            [
                str(STREAMLIT),
                "run",
                "app.py",
                "--server.headless",
                "true",
                "--server.address",
                BACK_HOST,
                "--server.port",
                str(BACK_PORT),
            ],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=log_handle,
            start_new_session=True,
        )
        deadline = time.time() + 90
        while time.time() < deadline:
            time.sleep(0.5)
            if backend_healthy():
                log("streamlit woke up on first request")
                return
        log("streamlit did not answer within 90 s")


def _splice(client: socket.socket, backend: socket.socket) -> None:
    sockets = [client, backend]
    try:
        while True:
            readable, _, _ = select.select(sockets, [], [], 30)
            if not readable:
                continue
            for source in readable:
                data = source.recv(65536)
                if not data:
                    return
                target = backend if source is client else client
                target.sendall(data)
    except OSError:
        pass
    finally:
        for sock in sockets:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _raw_request(self) -> bytes:
        lines = [self.raw_requestline.decode("latin-1").rstrip("\r\n")]
        for name, value in self.headers.items():
            lines.append(f"{name}: {value}")
        lines.append("")
        lines.append("")
        return "\r\n".join(lines).encode("latin-1")

    def _proxy_websocket(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        try:
            backend = socket.create_connection((BACK_HOST, BACK_PORT), timeout=10)
            backend.sendall(self._raw_request())
            answer = b""
            while b"\r\n\r\n" not in answer:
                chunk = backend.recv(65536)
                if not chunk:
                    raise ConnectionError("backend closed during handshake")
                answer += chunk
            self.connection.sendall(answer)
        except OSError:
            try:
                self.connection.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            except OSError:
                pass
            return
        _splice(self.connection, backend)

    def _proxy_http(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        request = urllib.request.Request(
            BACK_URL + self.path,
            data=body,
            method=self.command,
        )
        for header in ("Content-Type", "Accept"):
            value = self.headers.get(header)
            if value:
                request.add_header(header, value)
        try:
            ensure_backend()
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = response.read()
                status = response.status
                headers = response.headers
        except urllib.error.HTTPError as error:
            payload = error.read()
            status = error.code
            headers = error.headers
        except (urllib.error.URLError, OSError):
            payload = b"dashboard is waking up, retry in a few seconds\n"
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(status)
        skipped = {"connection", "transfer-encoding", "content-length", "server", "date"}
        for key, value in headers.items():
            if key.lower() not in skipped:
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _route(self) -> None:
        upgrade = (self.headers.get("Upgrade") or "").lower()
        connection = (self.headers.get("Connection") or "").lower()
        if upgrade == "websocket" or "upgrade" in connection:
            self._proxy_websocket()
        elif self.command == "HEAD":
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self._proxy_http()

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_HEAD = _route

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass


def main() -> None:
    listen_fds = int(os.environ.get("LISTEN_FDS", "0"))
    if listen_fds > 0:
        inherited = socket.socket(fileno=3)
        server = ThreadingHTTPServer.__new__(ThreadingHTTPServer)
        BaseServer_setup(server, inherited)
        source = "launchd socket"
    else:
        server = ThreadingHTTPServer((BACK_HOST, 8501), Handler)
        source = "own bind"
    log(f"wake-proxy up via {source}; backend :{BACK_PORT}")
    print(f"wake-proxy serving on inherited socket, backend {BACK_URL}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def BaseServer_setup(server: ThreadingHTTPServer, inherited: socket.socket) -> None:
    server.socket = inherited
    server.server_address = inherited.getsockname()
    server.RequestHandlerClass = Handler
    server.__initialized = True


if __name__ == "__main__":
    main()
