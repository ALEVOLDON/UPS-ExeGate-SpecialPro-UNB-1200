"""System Tray Manager for Windows using pystray and Pillow."""

import sys
import os
import time
import threading
import logging
from PIL import Image, ImageDraw

try:
    import pystray
    HAS_PYSTRAY = True
except Exception:
    HAS_PYSTRAY = False


def create_tray_image(color_hex: str = "#10b981", text_sub: str = "") -> Image.Image:
    """Generate a clean 64x64 RGBA icon with a battery symbol and dynamic status glow."""
    size = (64, 64)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Convert hex color to RGB tuple
    hex_clean = color_hex.lstrip('#')
    r = int(hex_clean[0:2], 16)
    g = int(hex_clean[2:4], 16)
    b = int(hex_clean[4:6], 16)

    # Outer circle background / glow
    draw.ellipse((4, 4, 60, 60), fill=(15, 23, 42, 230), outline=(r, g, b, 255), width=4)

    # Inner status dot
    draw.ellipse((22, 22, 42, 42), fill=(r, g, b, 255))

    # Lightning bolt accent in center (yellow/white)
    bolt_points = [(33, 10), (25, 32), (32, 32), (29, 54), (39, 30), (32, 30)]
    draw.polygon(bolt_points, fill=(255, 255, 255, 220))

    return img


class UPSTrayIcon:
    def __init__(self, on_open_dashboard=None, on_cancel_shutdown=None, on_exit=None):
        self.on_open_dashboard = on_open_dashboard
        self.on_cancel_shutdown = on_cancel_shutdown
        self.on_exit = on_exit
        
        self.icon = None
        self.running = False
        self.last_color = None
        self.current_title = "ExeGate UPS — Connecting..."

    def start(self):
        """Start the system tray icon in a dedicated daemon thread."""
        if not HAS_PYSTRAY:
            logging.warning("pystray is not available — Tray icon disabled.")
            return

        if self.running:
            return

        self.running = True
        thread = threading.Thread(target=self._run_tray, daemon=True)
        thread.start()

    def _run_tray(self):
        try:
            initial_img = create_tray_image("#9ca3af")
            menu = pystray.Menu(
                pystray.MenuItem("⚡ Open UPS Dashboard / Панель ИБП", self._handle_open, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ Cancel PC Shutdown / Отмена выключения", self._handle_cancel_shutdown),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("🚪 Exit Application / Выход", self._handle_exit)
            )

            self.icon = pystray.Icon(
                "exegate_ups_monitor",
                initial_img,
                title=self.current_title,
                menu=menu
            )
            logging.info("System Tray Icon started.")
            self.icon.run()
        except Exception as e:
            logging.error(f"Error running system tray icon: {e}")

    def update(self, ups_status: dict, shutdown_status: dict = None):
        """Update tray icon image and tooltip based on live telemetry."""
        if not self.icon or not self.running:
            return

        settings = shutdown_status.get("settings", {}) if shutdown_status else {}
        lang = settings.get("language", "en")

        color = ups_status.get("status_color", "#9ca3af")
        mode_title = (
            ups_status.get("mode_title", "Connecting...")
            if lang == "en"
            else ups_status.get("mode_title_ru", ups_status.get("mode_title", "Подключение..."))
        )
        in_v = ups_status.get("in_v", 0.0)
        batt_pct = ups_status.get("batt_pct", 0)
        
        if shutdown_status and shutdown_status.get("shutdown_active"):
            color = "#ef4444"
            sec = shutdown_status.get("seconds_left", 0)
            reason = shutdown_status.get("shutdown_reason", "")
            if lang == "en":
                tooltip = f"⚠️ PC SHUTDOWN IN {sec}s!\nReason: {reason}"
            else:
                tooltip = f"⚠️ ВЫКЛЮЧЕНИЕ ПК ЧЕРЕЗ {sec}с!\nПричина: {reason}"
        elif ups_status.get("connected"):
            if lang == "en":
                tooltip = f"ExeGate UNB-1200: {mode_title}\nInput: {in_v}V | Batt: {batt_pct}%"
            else:
                tooltip = f"ExeGate UNB-1200: {mode_title}\nВход: {in_v}V | АКБ: {batt_pct}%"
        else:
            color = "#ef4444"
            tooltip = "ExeGate UPS — USB Disconnected" if lang == "en" else "ExeGate ИБП — Нет связи по USB"

        self.current_title = tooltip

        try:
            self.icon.title = tooltip
            if color != self.last_color:
                self.last_color = color
                self.icon.icon = create_tray_image(color)
        except Exception as e:
            logging.debug(f"Error updating tray icon: {e}")

    def _handle_open(self, icon, item):
        if self.on_open_dashboard:
            self.on_open_dashboard()

    def _handle_cancel_shutdown(self, icon, item):
        if self.on_cancel_shutdown:
            self.on_cancel_shutdown()

    def _handle_exit(self, icon, item):
        self.stop()
        if self.on_exit:
            self.on_exit()
        else:
            os._exit(0)

    def stop(self):
        self.running = False
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
            self.icon = None
