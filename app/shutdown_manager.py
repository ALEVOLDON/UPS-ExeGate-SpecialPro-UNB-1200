"""Shutdown Manager for Windows Graceful Shutdown & Application Settings."""

import os
import sys
import json
import time
import subprocess
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(PROJECT_ROOT, "app_settings.json")

DEFAULT_SETTINGS = {
    "auto_shutdown_enabled": True,
    "shutdown_battery_pct": 15,
    "shutdown_delay_sec": 60,
    "toast_notif_enabled": True,
    "sound_enabled": True
}


class ShutdownManager:
    def __init__(self, notification_callback=None):
        self.settings = dict(DEFAULT_SETTINGS)
        self.notification_callback = notification_callback
        
        self.shutdown_active = False
        self.shutdown_start_time = 0.0
        self.shutdown_delay = 60
        self.seconds_left = 0
        self.shutdown_reason = ""
        
        self.load_settings()

    def load_settings(self) -> dict:
        """Load settings from JSON file."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as e:
                logging.error(f"Error loading settings file: {e}")
        return self.settings

    def save_settings(self, new_settings: dict) -> dict:
        """Save settings to JSON file."""
        self.settings.update(new_settings)
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logging.info("Settings saved successfully.")
        except Exception as e:
            logging.error(f"Error saving settings file: {e}")
        return self.settings

    def update_status(self, ups_data: dict) -> None:
        """
        Evaluate current UPS telemetry and trigger/abort shutdown as needed.
        """
        if not ups_data or not ups_data.get("connected"):
            return

        is_battery = ups_data.get("is_battery", False)
        batt_pct = ups_data.get("batt_pct", 100)
        
        # 1. Check if shutdown should be aborted because grid power was restored
        if self.shutdown_active and not is_battery:
            self.cancel_shutdown(reason="Питание от сети восстановлено")
            return

        # 2. Check if shutdown should be triggered
        if not self.shutdown_active and is_battery and self.settings.get("auto_shutdown_enabled"):
            threshold = self.settings.get("shutdown_battery_pct", 15)
            if batt_pct <= threshold:
                self.trigger_shutdown(
                    reason=f"Критический уровень разряда АКБ ({batt_pct}% <= {threshold}%)"
                )

        # 3. Update active countdown seconds_left
        if self.shutdown_active:
            elapsed = int(time.monotonic() - self.shutdown_start_time)
            remaining = max(0, self.shutdown_delay - elapsed)
            self.seconds_left = remaining

    def trigger_shutdown(self, reason: str = "Низкий заряд АКБ") -> bool:
        """Initiate Windows graceful shutdown with a countdown."""
        if self.shutdown_active:
            return True

        delay = int(self.settings.get("shutdown_delay_sec", 60))
        self.shutdown_active = True
        self.shutdown_start_time = time.monotonic()
        self.shutdown_delay = delay
        self.seconds_left = delay
        self.shutdown_reason = reason

        msg_comment = f"ExeGate UPS: {reason}. Выключение через {delay} сек."
        logging.warning(f"INITIATING SHUTDOWN: {reason} (delay={delay}s)")

        if sys.platform == "win32":
            try:
                cmd = f'shutdown /s /t {delay} /c "{msg_comment}"'
                subprocess.run(cmd, shell=True, check=True)
            except Exception as e:
                logging.error(f"Failed to execute shutdown command: {e}")

        if self.notification_callback and self.settings.get("toast_notif_enabled"):
            self.notification_callback(
                "⚠️ ВНИМАНИЕ: Автовыключение ПК!",
                f"{reason}. Выключение компьютера через {delay} секунд."
            )
        return True

    def cancel_shutdown(self, reason: str = "Запрос пользователя") -> bool:
        """Abort any active Windows shutdown command."""
        if not self.shutdown_active:
            # Still run shutdown /a in case system initiated it outside
            if sys.platform == "win32":
                try:
                    subprocess.run("shutdown /a", shell=True, capture_output=True)
                except Exception:
                    pass
            return True

        logging.info(f"ABORTING SHUTDOWN: {reason}")
        self.shutdown_active = False
        self.seconds_left = 0

        if sys.platform == "win32":
            try:
                subprocess.run("shutdown /a", shell=True, capture_output=True)
            except Exception as e:
                logging.error(f"Failed to execute shutdown /a command: {e}")

        if self.notification_callback and self.settings.get("toast_notif_enabled"):
            self.notification_callback(
                "✅ Автовыключение отменено",
                f"{reason}. Компьютер продолжит работу."
            )
        return True

    def get_status_dict(self) -> dict:
        """Get status dictionary for API snapshot."""
        return {
            "shutdown_active": self.shutdown_active,
            "seconds_left": self.seconds_left,
            "shutdown_delay": self.shutdown_delay,
            "shutdown_reason": self.shutdown_reason,
            "settings": self.settings
        }
