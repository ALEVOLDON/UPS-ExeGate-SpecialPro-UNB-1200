import sys
import os
import uvicorn
import webbrowser
import threading
import time

# Always run from the project folder (CSV, static paths, imports)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.netutil import DEFAULT_HOST, DEFAULT_PORT, port_in_use, port_busy_message


def open_browser():
    time.sleep(1.5)
    print(f"\n[+] Opening web dashboard at http://{DEFAULT_HOST}:{DEFAULT_PORT} ...")
    webbrowser.open(f"http://{DEFAULT_HOST}:{DEFAULT_PORT}")


def main():
    print("=" * 65)
    print(" ExeGate SpecialPro UNB-1200 Web Dashboard Server")
    print("=" * 65)
    print(f" [URL] http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    print(" [Log] ups_power_events.csv\n")

    if port_in_use():
        print("[!] " + port_busy_message().replace("\n\n", "\n"))
        sys.exit(1)

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        "app.server:app",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        reload=False,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
