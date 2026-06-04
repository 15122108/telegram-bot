import os
import signal
import subprocess
import sys
import threading
from http.server import HTTPServer

import admin_panel


def main() -> None:
    bot_process = subprocess.Popen([sys.executable, "bot.py"])

    def watch_bot() -> None:
        code = bot_process.wait()
        print(f"bot.py exited with code {code}", flush=True)
        os._exit(code or 1)

    threading.Thread(target=watch_bot, daemon=True).start()

    def shutdown(signum, frame) -> None:
        if bot_process.poll() is None:
            bot_process.terminate()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    port = int(os.environ.get("PORT", str(admin_panel.PORT)))
    print(f"Starting admin panel on 0.0.0.0:{port}", flush=True)
    HTTPServer((admin_panel.HOST, port), admin_panel.Handler).serve_forever()


if __name__ == "__main__":
    main()
