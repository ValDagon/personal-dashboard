#!/usr/bin/env python3
"""Run Streamlit detached from the parent shell (Cursor agent terminals).

Agent jobs keep sending SIGTERM to whatever they started on :8501. That is not
an app crash. This script starts a new session so the server is not a child of
Cursor. It does not install a login LaunchAgent.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("DASHBOARD_PORT", "8501"))
URL = f"http://127.0.0.1:{PORT}/"
URL = f"http://127.0.0.1:{PORT}/"
LOG_DIR = Path.home() / "Library" / "Logs" / "personal-dashboard"
PID_FILE = LOG_DIR / "streamlit.pid"
LOG_FILE = LOG_DIR / "serve.log"
STREAMLIT = ROOT / ".venv" / "bin" / "streamlit"


def _healthy() -> bool:
    try:
        with urlopen(URL, timeout=2) as response:
            return 200 <= response.status < 400
    except (URLError, OSError, TimeoutError):
        return False


def _pid_on_port() -> int | None:
    try:
        out = subprocess.check_output(
            ["lsof", "-tiTCP:%s" % PORT, "-sTCP:LISTEN"],
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return None
    if not out:
        return None
    return int(out.splitlines()[0])


def _stop() -> None:
    pid = _pid_on_port()
    if pid is None:
        print("not running")
        return
    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        time.sleep(0.1)
        if _pid_on_port() is None:
            break
    else:
        os.kill(pid, signal.SIGKILL)
    if PID_FILE.exists():
        PID_FILE.unlink()
    print(f"stopped pid {pid}")


def _start() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if _healthy():
        print(f"already up {URL}")
        return
    stale = _pid_on_port()
    if stale is not None:
        os.kill(stale, signal.SIGTERM)
        time.sleep(0.4)

    if not STREAMLIT.exists():
        sys.exit(f"missing {STREAMLIT}; create the venv first")

    log = open(LOG_FILE, "a", encoding="utf-8")
    proc = subprocess.Popen(
        [
            str(STREAMLIT),
            "run",
            "app.py",
            "--server.headless",
            "true",
            "--server.port",
            str(PORT),
        ],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=log,
        start_new_session=True,
    )
    PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    for _ in range(50):
        time.sleep(0.1)
        if _healthy():
            print(f"up {URL}")
            return
    sys.exit("daemon started but never answered HTTP")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--restart", action="store_true")
    args = parser.parse_args()
    if args.stop:
        _stop()
        return
    if args.restart:
        _stop()
        time.sleep(0.3)
    _start()


if __name__ == "__main__":
    main()
