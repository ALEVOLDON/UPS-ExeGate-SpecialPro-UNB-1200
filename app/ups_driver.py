import hid
import time
import threading
import logging
import csv
import os
from datetime import datetime
from collections import deque

from app.config import (
    VENDOR_ID, PRODUCT_ID, LOG_FILE, MAX_HISTORY_POINTS, MAX_EVENTS, POLL_INTERVAL_SEC
)
from app.protocol import parse_f_response, estimate_battery_pct
from app.notifications import send_notification
from app.sound_manager import play_sound
from app.shutdown_manager import ShutdownManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class UPSDriver:
    def __init__(self):
        self.dev = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self._seq = 0

        self.shutdown_manager = ShutdownManager(notification_callback=send_notification)


        self.current_status = {
            "connected": False,
            "timestamp": None,
            "time_short": "--:--:--",
            "seq": 0,
            "in_v": 0.0,
            "fault_v": 0.0,
            "out_v": 0.0,
            "load_pct": 0,
            "load_watts": 0,
            "freq": 0.0,
            "batt_v": 0.0,
            "batt_pct": 0,
            "temp": 0.0,
            "status_bits": "00000000",
            "raw_frame": "",
            "telemetry_frozen": False,
            "freeze_sec": 0.0,
            "is_battery": False,
            "is_batt_low": False,
            "is_avr": False,
            "is_avr_boost": False,
            "is_avr_trim": False,
            "mode_code": "DISCONNECTED",
            "mode_title": "Connecting...",
            "mode_title_ru": "Подключение...",
            "mode_desc": "Waiting for USB UPS connection",
            "mode_desc_ru": "Ожидание связи с ИБП по USB",
            "status_color": "#9ca3af"
        }

        self.history = deque(maxlen=MAX_HISTORY_POINTS)
        self.events = deque(maxlen=MAX_EVENTS)
        self.last_mode_code = None

        self.last_successful_read_time = time.monotonic()
        self.last_valid_data = None

        self.last_poll_time = time.monotonic()
        self.accumulated_kwh = float(self.shutdown_manager.settings.get("accumulated_kwh", 0.0))
        self.last_save_kwh_time = time.monotonic()

        self.energy_status = {
            "load_watts": 0.0,
            "self_watts": float(self.shutdown_manager.settings.get("self_consumption_watts", 15)),
            "total_watts": 0.0,
            "tariff": float(self.shutdown_manager.settings.get("electricity_tariff", 5.5)),
            "cost_per_hour": 0.0,
            "cost_per_day": 0.0,
            "cost_per_month": 0.0,
            "accumulated_kwh": self.accumulated_kwh,
            "accumulated_cost": 0.0,
        }

        self._init_csv()
        self._load_recent_events()

    def _init_csv(self):
        if not os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Mode", "Input_V", "Output_V", "Load_Pct", "Batt_V", "Temp_C", "Status_Bits"])
            except Exception as e:
                logging.error(f"Error creating CSV log file: {e}")

    def _load_recent_events(self):
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    rows = list(reader)
                    for r in rows[-MAX_EVENTS:]:
                        if len(r) >= 6 and r[0] and not r[0].startswith("Timestamp"):
                            try:
                                self.events.appendleft({
                                    "timestamp": r[0],
                                    "time_short": r[0].split(' ')[1] if ' ' in r[0] else r[0],
                                    "mode": r[1],
                                    "in_v": float(r[2]) if r[2] else 0.0,
                                    "out_v": float(r[3]) if r[3] else 0.0,
                                    "load_pct": int(float(r[4])) if r[4] else 0,
                                    "batt_v": float(r[5]) if r[5] else 0.0
                                })
                            except (ValueError, IndexError):
                                continue
            except Exception as e:
                logging.error(f"Error reading CSV events: {e}")

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._poll_loop, daemon=True)
            self.thread.start()
            logging.info("UPS background thread started.")

    def stop(self):
        self.running = False
        self._close_usb()

    def _close_usb(self):
        if self.dev:
            try:
                self.dev.close()
            except:
                pass
            self.dev = None

    def _connect_usb(self):
        self._close_usb()
        try:
            d = hid.device()
            d.open(VENDOR_ID, PRODUCT_ID)
            d.set_nonblocking(True)
            self.dev = d
            logging.info(f"Opened HID device {hex(VENDOR_ID)}:{hex(PRODUCT_ID)} (non-blocking)")
            return True
        except Exception as e:
            self.dev = None
            return False

    def _poll_loop(self):
        while self.running:
            t0 = time.monotonic()
            data, err = self._read_telemetry()
            now = datetime.now()
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            time_short = now.strftime("%H:%M:%S")

            with self.lock:
                self._seq += 1
                seq = self._seq

                if data:
                    self.last_successful_read_time = time.monotonic()
                    self.last_valid_data = data
                    self.current_status = {
                        "connected": True,
                        "telemetry_frozen": False,
                        "freeze_sec": 0.0,
                        "timestamp": now_str,
                        "time_short": time_short,
                        "seq": seq,
                        **data
                    }

                    self.history.append({
                        "time": time_short,
                        "in_v": data["in_v"],
                        "out_v": data["out_v"],
                        "load_pct": data["load_pct"],
                        "batt_v": data["batt_v"],
                        "batt_pct": data["batt_pct"]
                    })

                    mode_code = data["mode_code"]
                    if mode_code != self.last_mode_code:
                        if self.last_mode_code is not None:
                            event_obj = {
                                "timestamp": now_str,
                                "time_short": time_short,
                                "mode": data["mode_title"],
                                "in_v": data["in_v"],
                                "out_v": data["out_v"],
                                "load_pct": data["load_pct"],
                                "batt_v": data["batt_v"],
                            }
                            self.events.appendleft(event_obj)
                            self._append_csv(data)
                            logging.info(f"MODE CHANGE: {self.last_mode_code} -> {mode_code} | in={data['in_v']}V out={data['out_v']}V")
                            
                            # Native Toast Notification on mode changes
                            if self.shutdown_manager.settings.get("toast_notif_enabled"):
                                lang = self.shutdown_manager.settings.get("language", "en")
                                title_mode = data.get("mode_title") if lang == "en" else data.get("mode_title_ru", data.get("mode_title"))
                                notif_title = f"UPS: {title_mode}"
                                notif_body = (
                                    f"Input: {data['in_v']}V -> Output: {data['out_v']}V (Batt: {data['batt_pct']}%)"
                                    if lang == "en"
                                    else f"Входное напряжение: {data['in_v']}V -> Выходное: {data['out_v']}V (АКБ: {data['batt_pct']}%)"
                                )
                                send_notification(notif_title, notif_body)
                        self.last_mode_code = mode_code

                else:
                    unresponsive_sec = time.monotonic() - self.last_successful_read_time
                    if unresponsive_sec <= 4.0 and self.last_valid_data:
                        # Grace period: keep last valid values visible during brief USB glitches
                        self.current_status.update({
                            "connected": True,
                            "telemetry_frozen": True,
                            "freeze_sec": round(unresponsive_sec, 1),
                            "timestamp": now_str,
                            "time_short": time_short,
                            "seq": seq
                        })
                    else:
                        self.current_status.update({
                            "connected": False,
                            "telemetry_frozen": False,
                            "freeze_sec": 0.0,
                            "timestamp": now_str,
                            "time_short": time_short,
                            "seq": seq,
                            "mode_code": "DISCONNECTED",
                            "mode_title": "Reconnecting...",
                            "mode_title_ru": "Восстановление связи...",
                            "mode_desc": err or "Reconnecting to USB UPS...",
                            "mode_desc_ru": err or "Переподключение к USB ИБП...",
                            "status_color": "#ef4444"
                        })

                # Update Shutdown Manager
                self.shutdown_manager.update_status(self.current_status)

                # Update Energy & Cost calculations
                now_mono = time.monotonic()
                dt = now_mono - self.last_poll_time
                self.last_poll_time = now_mono

                settings = self.shutdown_manager.settings
                self_watts = float(settings.get("self_consumption_watts", 15))
                tariff = float(settings.get("electricity_tariff", 5.5))

                connected = self.current_status.get("connected", False)
                load_watts = float(self.current_status.get("load_watts", 0)) if connected else 0.0
                total_watts = (load_watts + self_watts) if connected else 0.0

                if connected and 0 < dt < 10.0:
                    kwh_delta = (total_watts * dt) / 3600000.0
                    self.accumulated_kwh += kwh_delta

                    if now_mono - self.last_save_kwh_time > 30.0:
                        self.last_save_kwh_time = now_mono
                        self.shutdown_manager.save_settings({"accumulated_kwh": round(self.accumulated_kwh, 4)})

                cost_per_hour = (total_watts / 1000.0) * tariff
                cost_per_day = cost_per_hour * 24.0
                cost_per_month = cost_per_day * 30.0
                accumulated_cost = self.accumulated_kwh * tariff

                self.energy_status = {
                    "load_watts": round(load_watts, 1),
                    "self_watts": round(self_watts, 1),
                    "total_watts": round(total_watts, 1),
                    "tariff": round(tariff, 2),
                    "cost_per_hour": round(cost_per_hour, 2),
                    "cost_per_day": round(cost_per_day, 2),
                    "cost_per_month": round(cost_per_month, 2),
                    "accumulated_kwh": round(self.accumulated_kwh, 4),
                    "accumulated_cost": round(accumulated_cost, 2),
                }

            elapsed = time.monotonic() - t0
            time.sleep(max(0.1, POLL_INTERVAL_SEC - elapsed))

    def reset_accumulated_kwh(self):
        with self.lock:
            self.accumulated_kwh = 0.0
            self.shutdown_manager.save_settings({"accumulated_kwh": 0.0})
            if hasattr(self, "energy_status"):
                self.energy_status["accumulated_kwh"] = 0.0
                self.energy_status["accumulated_cost"] = 0.0

    def _read_telemetry(self):
        if not self.dev:
            if not self._connect_usb():
                return None, "USB ИБП не найден (0665:5161)"

        try:
            # Полностью вычитываем все старые пакеты из буфера Windows (чтобы не было "лагов" и зависаний данных)
            for _ in range(1024):
                if not self.dev.read(64):
                    break

            # Send exactly 65 bytes padded with spaces to bypass hidapi's zero-padding
            # This prevents the Cypress chip UART from crashing on the 0x00 bytes
            cmd = b'\x00' + b'F\r'.ljust(64, b' ')
            self.dev.write(cmd)
        except Exception as e:
            logging.warning(f"USB Write error (reconnecting): {e}")
            self._connect_usb()
            return None, f"Ошибка записи USB: {e}"

        time.sleep(0.08)
        full_res = b""
        start_t = time.time()

        while time.time() - start_t < 0.6:
            try:
                buf = self.dev.read(64)
                if buf:
                    full_res += bytes(buf)
                    if b'\r' in full_res:
                        break
            except Exception as e:
                logging.warning(f"USB Read error (reconnecting): {e}")
                self._connect_usb()
                break
            time.sleep(0.02)
            
        if not full_res:
            self._connect_usb()
            return None, "Нет ответа на команду F"

        try:
            text = full_res.decode('ascii', errors='ignore')
            parsed = parse_f_response(text)
            if not parsed:
                return None, f"Формат ответа не распознан: '{text.strip()}'"
            return parsed, None
        except Exception as e:
            return None, f"Ошибка декодирования: {e}"


    def _append_csv(self, data):
        try:
            with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    data["mode_title"],
                    data["in_v"],
                    data["out_v"],
                    data["load_pct"],
                    data["batt_v"],
                    data["temp"],
                    data["status_bits"]
                ])
        except Exception as e:
            logging.error(f"Error appending to CSV: {e}")

    def get_snapshot(self):
        with self.lock:
            return {
                "status": dict(self.current_status),
                "history": list(self.history),
                "events": list(self.events),
                "shutdown": self.shutdown_manager.get_status_dict(),
                "energy": dict(getattr(self, "energy_status", {}))
            }

