import sys
import os
import time
import threading
import traceback

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
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ExeGate.UPSMonitor.SpecialPro.UNB1200")
    except Exception:
        pass

from app.netutil import DEFAULT_HOST, DEFAULT_PORT, port_in_use


def show_error(title: str, message: str) -> None:
    """Show a visible error even when launched via pythonw (no console)."""
    print(f"[!] {title}: {message}")
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)  # MB_ICONERROR
            return
        except Exception:
            pass
    try:
        sys.stderr.write(f"{title}\n{message}\n")
    except Exception:
        pass


def set_windows_taskbar_icon(window_title: str, icon_path: str):
    if sys.platform != "win32" or not os.path.exists(icon_path):
        return

    def _apply():
        import ctypes

        for _ in range(25):
            time.sleep(0.2)
            hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
            if hwnd:
                WM_SETICON = 0x0080
                ICON_SMALL = 0
                ICON_BIG = 1
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x00000010

                h_icon_big = ctypes.windll.user32.LoadImageW(
                    0, icon_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE
                )
                h_icon_small = ctypes.windll.user32.LoadImageW(
                    0, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE
                )
                if h_icon_big:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_icon_big)
                if h_icon_small:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_icon_small)
                break

    threading.Thread(target=_apply, daemon=True).start()


def start_server(app):
    import uvicorn

    uvicorn.run(app, host=DEFAULT_HOST, port=DEFAULT_PORT, log_level="warning")


def wait_for_server(timeout: float = 8.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_in_use():
            return True
        time.sleep(0.15)
    return False


def open_window():
    import webview

    title = "ExeGate SpecialPro — UPS Monitor"
    icon_path = os.path.join(APP_DIR, "assets", "app_icon.ico")
    set_windows_taskbar_icon(title, icon_path)

    window = webview.create_window(
        title=title,
        url=f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/?v={int(time.time())}",
        width=1220,
        height=820,
        min_size=(940, 640),
        background_color="#0b0f19",
        resizable=True,
        text_select=False,
    )
    print(f"[+] Desktop window -> http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    webview.start()
    return window


def start_tray_updater(tray_icon, ups_driver_inst):
    def update_loop():
        while True:
            try:
                snap = ups_driver_inst.get_snapshot()
                ups_status = snap.get("status", {})
                shutdown_status = snap.get("shutdown", {})
                tray_icon.update(ups_status, shutdown_status)
            except Exception:
                pass
            time.sleep(1.0)

    t = threading.Thread(target=update_loop, daemon=True)
    t.start()


def main():
    print("=" * 65)
    print(" ExeGate SpecialPro Desktop Application (UNB & Smart LLB)")
    print("=" * 65)

    try:
        import webview  # noqa: F401
    except ImportError as e:
        show_error(
            "UPS Monitor — нет зависимости",
            f"Не удалось импортировать pywebview: {e}\n\n"
            "Установите зависимости:\n"
            "  pip install -r requirements.txt",
        )
        sys.exit(1)

    already_running = port_in_use()

    if already_running:
        # Attach to the already running dashboard instead of failing
        print(f"[*] Port {DEFAULT_PORT} busy — opening window on existing server.")
        try:
            open_window()
        except Exception as e:
            show_error(
                "UPS Monitor — ошибка окна",
                f"{e}\n\n{traceback.format_exc()}",
            )
            sys.exit(1)
        return

    try:
        from app.server import app as fastapi_app, ups_driver
        from app.tray_icon import UPSTrayIcon
    except ImportError as e:
        show_error(
            "UPS Monitor — нет зависимости",
            f"Не удалось импортировать сервер/трей: {e}\n\n"
            "Установите зависимости:\n"
            "  pip install -r requirements.txt",
        )
        sys.exit(1)

    # Initialize System Tray Icon
    def on_open():
        import webbrowser
        webbrowser.open(f"http://{DEFAULT_HOST}:{DEFAULT_PORT}")

    def on_cancel():
        ups_driver.shutdown_manager.cancel_shutdown(reason="Отмена из меню трея")

    tray = UPSTrayIcon(
        on_open_dashboard=on_open,
        on_cancel_shutdown=on_cancel,
        on_exit=lambda: os._exit(0)
    )
    tray.start()
    start_tray_updater(tray, ups_driver)

    server_thread = threading.Thread(
        target=start_server, args=(fastapi_app,), daemon=True
    )
    server_thread.start()

    if not wait_for_server():
        show_error(
            "UPS Monitor — сервер не запустился",
            f"Не удалось поднять http://{DEFAULT_HOST}:{DEFAULT_PORT} за отведённое время.\n"
            "Проверьте, что порт свободен и зависимости установлены.",
        )
        sys.exit(1)

    try:
        open_window()
    except Exception as e:
        show_error(
            "UPS Monitor — ошибка окна",
            f"{e}\n\n{traceback.format_exc()}",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

