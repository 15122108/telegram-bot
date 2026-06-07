import os
import signal
import subprocess
import sys
import threading
from http.server import HTTPServer
from urllib.request import urlopen

import admin_panel


def main() -> None:
    stop_event = threading.Event()
    process_lock = threading.Lock()
    bot_process: subprocess.Popen | None = None

    def start_bot() -> subprocess.Popen:
        print("Starting bot.py", flush=True)
        return subprocess.Popen([sys.executable, "bot.py"])

    def bot_watchdog() -> None:
        nonlocal bot_process
        restart_delay = 2
        while not stop_event.is_set():
            with process_lock:
                bot_process = start_bot()
                current_process = bot_process
            code = current_process.wait()
            if stop_event.is_set():
                break
            print(f"bot.py exited with code {code}; restarting in {restart_delay}s", flush=True)
            stop_event.wait(restart_delay)
            restart_delay = min(restart_delay * 2, 30)

    def keepalive_loop() -> None:
        enabled = os.environ.get("KEEPALIVE_ENABLED", "1").strip() != "0"
        if not enabled:
            return
        base_url = os.environ.get("KEEPALIVE_URL") or os.environ.get("RENDER_EXTERNAL_URL") or ""
        if not base_url:
            print("Keepalive disabled: KEEPALIVE_URL/RENDER_EXTERNAL_URL not set", flush=True)
            return
        url = base_url.rstrip("/") + "/health"
        try:
            interval = max(60, int(os.environ.get("KEEPALIVE_INTERVAL_SECONDS", "600")))
        except ValueError:
            interval = 600
        print(f"Keepalive enabled: {url} every {interval}s", flush=True)
        while not stop_event.wait(interval):
            try:
                with urlopen(url, timeout=10) as response:
                    response.read(64)
                print("Keepalive ping ok", flush=True)
            except Exception as exc:
                print(f"Keepalive ping failed: {exc}", flush=True)

    threading.Thread(target=bot_watchdog, daemon=True).start()
    threading.Thread(target=keepalive_loop, daemon=True).start()

    def shutdown(signum, frame) -> None:
        stop_event.set()
        with process_lock:
            current_process = bot_process
        if current_process and current_process.poll() is None:
            current_process.terminate()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    port = int(os.environ.get("PORT", str(admin_panel.PORT)))
    print(f"Starting admin panel on 0.0.0.0:{port}", flush=True)
    HTTPServer((admin_panel.HOST, port), admin_panel.Handler).serve_forever()


if __name__ == "__main__":
    main()
