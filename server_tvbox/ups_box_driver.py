import os

import sys

import time

import glob

import fcntl

import ctypes

import threading

import logging

import csv

import json

from datetime import datetime

from collections import deque

import requests



logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")



# Linux USBDEVFS ioctl definitions

class usbdevfs_ctrltransfer(ctypes.Structure):

    _fields_ = [

        ('bRequestType', ctypes.c_uint8),

        ('bRequest', ctypes.c_uint8),

        ('wValue', ctypes.c_uint16),

        ('wIndex', ctypes.c_uint16),

        ('wLength', ctypes.c_uint16),

        ('timeout', ctypes.c_uint32),

        ('data', ctypes.c_void_p),

    ]



class usbdevfs_bulktransfer(ctypes.Structure):

    _fields_ = [

        ('ep', ctypes.c_uint32),

        ('len', ctypes.c_uint32),

        ('timeout', ctypes.c_uint32),

        ('data', ctypes.c_void_p),

    ]



USBDEVFS_CLAIMINTERFACE = (2 << 30) | (ord('U') << 8) | 15 | (4 << 16)

USBDEVFS_CONTROL = (3 << 30) | (ord('U') << 8) | 0 | (ctypes.sizeof(usbdevfs_ctrltransfer) << 16)

USBDEVFS_BULK = (3 << 30) | (ord('U') << 8) | 2 | (ctypes.sizeof(usbdevfs_bulktransfer) << 16)



def normalize_battery_voltage(batt_v: float, batt_mode: str = "auto") -> tuple:

    try:

        v = float(batt_v)

    except (TypeError, ValueError):

        return 0.0, 1.0



    mode = (batt_mode or "auto").lower()

    if mode == "24v":

        divisor = 2.0

    elif mode == "12v":

        divisor = 1.0

    else:  # auto

        if v > 18.0:

            divisor = 2.0

        else:

            divisor = 1.0

    return (v / divisor if divisor > 0 else v), divisor



def estimate_battery_pct(batt_v: float, on_battery: bool, is_batt_low: bool, batt_mode: str = "auto") -> int:

    norm_v, _ = normalize_battery_voltage(batt_v, batt_mode)

    v = norm_v



    if is_batt_low:

        return max(0, min(10, int(round((v - 10.0) * 8))))



    if not on_battery:

        if v >= 12.70: return 100

        if v >= 12.55: return 97

        if v >= 12.40: return 92

        if v >= 12.25: return 85

        if v >= 12.10: return 75

        if v >= 11.95: return 65

        if v >= 11.80: return 50

        if v >= 11.55: return 35

        if v >= 11.25: return 20

        return 10



    points = [

        (12.60, 100), (12.45, 90), (12.30, 80), (12.15, 70),

        (12.00, 55), (11.80, 40), (11.55, 25), (11.25, 12), (10.20, 0)

    ]

    if v >= points[0][0]: return 100

    if v <= points[-1][0]: return 0

    for i in range(len(points) - 1):

        v_hi, p_hi = points[i]

        v_lo, p_lo = points[i + 1]

        if v_lo <= v <= v_hi:

            span = v_hi - v_lo

            t = (v - v_lo) / span if span else 0.0

            return int(round(p_lo + t * (p_hi - p_lo)))

    return 0



class BoxUPSDriver:

    def __init__(self, data_dir="/data/data/com.termux/files/home/exegate_ups_monitor"):

        self.data_dir = data_dir

        os.makedirs(self.data_dir, exist_ok=True)

        self.log_file = os.path.join(self.data_dir, "ups_power_events.csv")

        self.chat_file = os.path.join(self.data_dir, "telegram_chats.json")

        self.fd = None

        self.running = False

        self.thread = None

        self.tg_thread = None

        self.lock = threading.Lock()

        self._seq = 0

        self.rated_watts = 750



        # Dedicated ExeGate UPS Telegram Bot
        self.config_file = os.path.join(self.data_dir, "bot_config.json")
        self.tg_token = os.environ.get("TG_BOT_TOKEN", "")
        self.tg_chat_ids = set()
        self.tg_enabled = True
        self._load_config()
        self._load_chat_ids()



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

            "rated_watts": self.rated_watts,

            "ups_model_name": "ExeGate SpecialPro UNB-1200",

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



        self.history = deque(maxlen=120)

        self.events = deque(maxlen=100)

        self.last_mode_code = None

        self.last_poll_time = time.monotonic()

        self.accumulated_kwh = 0.0

        self.energy_status = {

            "load_watts": 0.0,

            "self_watts": 15.0,

            "total_watts": 0.0,

            "tariff": 1.94,

            "cost_per_hour": 0.0,

            "cost_per_day": 0.0,

            "cost_per_month": 0.0,

            "accumulated_kwh": 0.0,

            "accumulated_cost": 0.0

        }



        self._load_csv_events()



    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if not self.tg_token:
                        self.tg_token = cfg.get("telegram_bot_token", "")
                    chats = cfg.get("telegram_chat_ids", [])
                    if isinstance(chats, list):
                        self.tg_chat_ids.update(str(x) for x in chats)
            except Exception as e:
                logging.error(f"Error loading bot_config.json: {e}")
        self.tg_enabled = bool(self.tg_token)

    def _load_chat_ids(self):

        if os.path.exists(self.chat_file):

            try:

                with open(self.chat_file, "r", encoding="utf-8") as f:

                    data = json.load(f)

                    if isinstance(data, list):

                        self.tg_chat_ids.update(str(x) for x in data)

            except Exception as e:

                logging.error(f"Error loading chat ids: {e}")



    def _save_chat_ids(self):

        try:

            with open(self.chat_file, "w", encoding="utf-8") as f:

                json.dump(list(self.tg_chat_ids), f)

        except Exception as e:

            logging.error(f"Error saving chat ids: {e}")



    def _load_csv_events(self):

        if not os.path.exists(self.log_file):

            return

        try:

            with open(self.log_file, "r", encoding="utf-8") as f:

                reader = csv.reader(f)

                header = next(reader, None)

                rows = list(reader)

                for r in rows[-100:]:

                    if len(r) >= 6 and r[0] and not r[0].startswith("Timestamp"):

                        self.events.appendleft({

                            "timestamp": r[0],

                            "time_short": r[0].split(" ")[1] if " " in r[0] else r[0],

                            "mode": r[1],

                            "in_v": float(r[2]) if r[2] else 0.0,

                            "out_v": float(r[3]) if r[3] else 0.0,

                            "load_pct": int(float(r[4])) if r[4] else 0,

                            "batt_v": float(r[5]) if r[5] else 0.0

                        })

        except Exception as e:

            logging.error(f"Error loading CSV events: {e}")



    def _find_usb_device(self):

        for p in glob.glob('/sys/bus/usb/devices/*'):

            try:

                with open(os.path.join(p, 'idVendor')) as f: v = f.read().strip()

                with open(os.path.join(p, 'idProduct')) as f: pr = f.read().strip()

                if v == '0665' and pr == '5161':

                    intf_name = f"{os.path.basename(p)}:1.0"

                    unbind_path = "/sys/bus/usb/drivers/usbhid/unbind"

                    if os.path.exists(f"/sys/bus/usb/drivers/usbhid/{intf_name}"):

                        try:

                            with open(unbind_path, "w") as uf:

                                uf.write(intf_name)

                            logging.info(f"Unbound {intf_name} from usbhid")

                        except Exception:

                            pass

                    with open(os.path.join(p, 'busnum')) as f: bus = int(f.read().strip())

                    with open(os.path.join(p, 'devnum')) as f: dev = int(f.read().strip())

                    return f'/dev/bus/usb/{bus:03d}/{dev:03d}'

            except Exception:

                pass

        return None



    def _connect(self):
        if self.fd is not None:
            try: os.close(self.fd)
            except Exception: pass
            self.fd = None

        dev_path = self._find_usb_device()
        if not dev_path or not os.path.exists(dev_path):
            return False

        try:
            try:
                if os.path.exists("/sys/bus/usb/devices/4-1:1.0/driver"):
                    os.system("su 0 sh -c 'echo -n 4-1:1.0 > /sys/bus/usb/drivers/usbhid/unbind' >/dev/null 2>&1")
                    time.sleep(0.1)
            except Exception:
                pass

            self.fd = os.open(dev_path, os.O_RDWR)
            intf = ctypes.c_uint32(0)
            try:
                fcntl.ioctl(self.fd, USBDEVFS_CLAIMINTERFACE, intf)
            except Exception:
                os.system("su 0 sh -c 'echo -n 4-1:1.0 > /sys/bus/usb/drivers/usbhid/unbind' >/dev/null 2>&1")
                time.sleep(0.1)
                fcntl.ioctl(self.fd, USBDEVFS_CLAIMINTERFACE, intf)

            logging.info(f"Connected and claimed interface on {dev_path}")
            return True
        except Exception as e:
            logging.error(f"Error opening {dev_path}: {e}")
            if self.fd is not None:
                try: os.close(self.fd)
                except Exception: pass
            self.fd = None
            return False

    def _query_q1(self):

        if self.fd is None:

            if not self._connect():

                return None, "UPS disconnected"



        try:

            cmd = b'Q1\r'.ljust(8, b'\x00')

            c_buf = ctypes.create_string_buffer(cmd, 8)

            ctrl = usbdevfs_ctrltransfer()

            ctrl.bRequestType = 0x21

            ctrl.bRequest = 0x09

            ctrl.wValue = 0x0200

            ctrl.wIndex = 0

            ctrl.wLength = 8

            ctrl.timeout = 2000

            ctrl.data = ctypes.cast(c_buf, ctypes.c_void_p).value

            fcntl.ioctl(self.fd, USBDEVFS_CONTROL, ctrl)



            full_resp = b''

            for _ in range(10):

                in_buf = ctypes.create_string_buffer(8)

                bulk = usbdevfs_bulktransfer()

                bulk.ep = 0x81

                bulk.len = 8

                bulk.timeout = 1000

                bulk.data = ctypes.cast(in_buf, ctypes.c_void_p).value

                fcntl.ioctl(self.fd, USBDEVFS_BULK, bulk)

                chunk = bytes(in_buf.raw[:8])

                full_resp += chunk

                if b'\r' in full_resp:

                    break



            raw_str = full_resp.decode('latin1', errors='ignore').strip()

            return self._parse_telemetry(raw_str)

        except Exception as e:

            logging.warning(f"USB query error: {e}")

            if self.fd is not None:

                try: os.close(self.fd)

                except Exception: pass

                self.fd = None

            return None, str(e)



    def _parse_telemetry(self, raw_text):

        text = raw_text.strip()

        if '(' in text:

            text = text[text.find('(') + 1:]

        else:

            return None, f"Malformed frame: {raw_text}"



        for end_char in ('\r', '\n', '\0'):

            if end_char in text:

                text = text[:text.find(end_char)]



        parts = text.split()

        if len(parts) < 8:

            return None, f"Not enough fields: {text}"



        try:

            in_v = float(parts[0])

            fault_v = float(parts[1])

            out_v = float(parts[2])

            load_pct = int(parts[3])

            freq = float(parts[4])

            batt_v = float(parts[5])

            temp = float(parts[6])

            status_bits = parts[7][:8].ljust(8, '0')



            is_battery = status_bits[0] == '1'

            is_batt_low = status_bits[1] == '1'

            avr_bit = status_bits[2] == '1'



            v_diff = out_v - in_v

            is_avr_boost = (not is_battery) and (avr_bit or v_diff >= 12 or (in_v > 0 and in_v <= 210 and out_v > in_v + 6))

            is_avr_trim = (not is_battery) and ((avr_bit and v_diff <= -12) or (in_v >= 245 and v_diff <= -8))

            is_avr = is_avr_boost or is_avr_trim



            batt_pct = estimate_battery_pct(batt_v, is_battery, is_batt_low)

            load_watts = int(round((load_pct / 100.0) * self.rated_watts))



            if is_battery:

                if is_batt_low:

                    mode_code = "BATT_LOW"

                    mode_title = "BATTERY LOW"

                    mode_title_ru = "Батарея разряжена!"

                    mode_desc = "Critical battery level!"

                    mode_desc_ru = "Критически низкий заряд АКБ!"

                    status_color = "#ef4444"

                else:

                    mode_code = "BATTERY"

                    mode_title = "ON BATTERY"

                    mode_title_ru = "От батареи"

                    mode_desc = "AC disconnected, running on inverter"

                    mode_desc_ru = "Сеть 220В отключена, работа от инвертора"

                    status_color = "#f59e0b"

            elif is_avr_boost:

                mode_code = "AVR_BOOST"

                mode_title = "[AVR] BOOST (+)"

                mode_title_ru = "AVR: Повышение (+)"

                mode_desc = f"Voltage sag ({in_v}V), AVR boosting output"

                mode_desc_ru = f"Просадка сети ({in_v}В), стабилизатор повышает"

                status_color = "#3b82f6"

            elif is_avr_trim:

                mode_code = "AVR_TRIM"

                mode_title = "[AVR] TRIM (-)"

                mode_title_ru = "AVR: Понижение (-)"

                mode_desc = f"Overvoltage ({in_v}V), AVR trimming output"

                mode_desc_ru = f"Перенапряжение ({in_v}В), стабилизатор понижает"

                status_color = "#8b5cf6"

            else:

                mode_code = "ONLINE"

                mode_title = "NORMAL (LINE)"

                mode_title_ru = "Сеть в норме"

                mode_desc = "Line normal, bypass active"

                mode_desc_ru = "Напряжение в норме, питание от сети"

                status_color = "#10b981"



            return {

                "in_v": in_v,

                "fault_v": fault_v,

                "out_v": out_v,

                "load_pct": load_pct,

                "load_watts": load_watts,

                "freq": freq,

                "batt_v": batt_v,

                "batt_pct": batt_pct,

                "temp": temp,

                "status_bits": status_bits,

                "raw_frame": raw_text,

                "is_battery": is_battery,

                "is_batt_low": is_batt_low,

                "is_avr": is_avr,

                "is_avr_boost": is_avr_boost,

                "is_avr_trim": is_avr_trim,

                "mode_code": mode_code,

                "mode_title": mode_title,

                "mode_title_ru": mode_title_ru,

                "mode_desc": mode_desc,

                "mode_desc_ru": mode_desc_ru,

                "status_color": status_color

            }, None

        except Exception as e:

            return None, f"Parse error: {e}"



    def send_telegram(self, message: str, custom_keyboard: bool = True, target_chat: str = None):

        if not self.tg_enabled or not self.tg_token:

            return

        def _send():

            url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"

            payload = {

                "text": message,

                "parse_mode": "HTML"

            }

            if custom_keyboard:

                payload["reply_markup"] = {

                    "keyboard": [

                        [{"text": "⚡ Статус сети и ИБП"}, {"text": "🔋 Заряд АКБ"}],

                        [{"text": "📈 Напряжение в розетке"}, {"text": "💡 Нагрузка (Вт)"}]

                    ],

                    "resize_keyboard": True

                }

            chats = [target_chat] if target_chat else list(self.tg_chat_ids)

            for chat_id in chats:

                try:

                    payload["chat_id"] = str(chat_id).strip()

                    requests.post(url, json=payload, timeout=5)

                except Exception as e:

                    logging.warning(f"Telegram send error: {e}")

        threading.Thread(target=_send, daemon=True).start()



    def _format_status_message(self):

        st = self.current_status

        return (

            f"⚡ <b>Монитор питания — ExeGate SpecialPro</b>\n\n"

            f"🔌 Режим: <b>{st.get('mode_title_ru', 'Сеть')}</b>\n"

            f"📉 Входная сеть: <b>{st.get('in_v', 0.0)} В</b>\n"

            f"⚡ Выход ИБП: <b>{st.get('out_v', 0.0)} В</b>\n"

            f"🔋 Заряд аккумулятора: <b>{st.get('batt_pct', 0)}%</b> ({st.get('batt_v', 0.0)} В)\n"

            f"💡 Текущая нагрузка: <b>{st.get('load_pct', 0)}%</b> (~{st.get('load_watts', 0)} Вт)\n"

            f"🌡️ Температура: {st.get('temp', 0.0)} °C\n"

            f"🕒 Время замера: {st.get('time_short', '--:--:--')}\n"

            f"🌐 Веб-дашборд: <code>http://192.168.0.103:8089</code>"

        )



    def _telegram_bot_loop(self):

        offset = 0

        while self.running:

            try:

                url = f"https://api.telegram.org/bot{self.tg_token}/getUpdates?offset={offset}&timeout=15"

                r = requests.get(url, timeout=20)

                if r.status_code == 200:

                    data = r.json()

                    for upd in data.get("result", []):

                        offset = upd["update_id"] + 1

                        msg = upd.get("message", {})

                        chat = msg.get("chat", {})

                        cid = str(chat.get("id", ""))

                        text = (msg.get("text") or "").strip().lower()



                        if cid and cid not in self.tg_chat_ids:

                            self.tg_chat_ids.add(cid)

                            self._save_chat_ids()

                            logging.info(f"Added new Telegram chat ID: {cid}")



                        st = self.current_status

                        if text in ("/start", "/help"):

                            welcome = (

                                f"👋 <b>Привет! Я бот мониторинга твоего ИБП ExeGate SpecialPro.</b>\n\n"

                                f"Я круглосуточно слежу за твоей электросетью и сразу сообщу, если отключится свет или просядет вольтаж.\n\n"

                                f"{self._format_status_message()}"

                            )

                            self.send_telegram(welcome, target_chat=cid)

                        elif any(k in text for k in ["заряд", "батаре", "акб", "batt"]):

                            msg_text = (

                                f"🔋 <b>Состояние аккумулятора ИБП:</b>\n\n"

                                f"• Заряд АКБ: <b>{st.get('batt_pct', 0)}%</b>\n"

                                f"• Напряжение: <b>{st.get('batt_v', 0.0)} В</b>\n"

                                f"• Температура: <b>{st.get('temp', 0.0)} °C</b>\n"

                                f"• Режим: <b>{st.get('mode_title_ru', 'Норма')}</b>"

                            )

                            self.send_telegram(msg_text, target_chat=cid)

                        elif any(k in text for k in ["розетк", "вольт", "напряжен", "сеть", "volt"]):

                            msg_text = (

                                f"📈 <b>Напряжение электросети:</b>\n\n"

                                f"• Входная сеть (розетка): <b>{st.get('in_v', 0.0)} В</b>\n"

                                f"• Выход ИБП на приборы: <b>{st.get('out_v', 0.0)} В</b>\n"

                                f"• Частота: <b>{st.get('freq', 50.0)} Гц</b>\n"

                                f"• Статус AVR: <b>{st.get('mode_title_ru', 'Сеть')}</b>"

                            )

                            self.send_telegram(msg_text, target_chat=cid)

                        elif any(k in text for k in ["нагруз", "ватт", "load", "watt", "энерг", "руб"]):

                            en = self.energy_status

                            msg_text = (

                                f"💡 <b>Энергопотребление и нагрузка:</b>\n\n"

                                f"• Нагрузка: <b>{st.get('load_pct', 0)}%</b> (~<b>{st.get('load_watts', 0)} Вт</b>)\n"

                                f"• Номинал ИБП: <b>{self.rated_watts} Вт</b>\n"

                                f"• Расход в час: ~<b>{en.get('cost_per_hour', 0.0)} руб</b>\n"

                                f"• Расход в сутки: ~<b>{en.get('cost_per_day', 0.0)} руб</b>\n"

                                f"• Накоплено: <b>{en.get('accumulated_kwh', 0.0)} кВт·ч</b> ({en.get('accumulated_cost', 0.0)} руб)"

                            )

                            self.send_telegram(msg_text, target_chat=cid)

                        elif any(k in text for k in ["статус", "status", "ups", "ибп", "power", "инфо"]):

                            self.send_telegram(self._format_status_message(), target_chat=cid)

            except Exception as e:

                time.sleep(2)

            time.sleep(1)



    def start(self):

        if not self.running:

            self.running = True

            self.thread = threading.Thread(target=self._poll_loop, daemon=True)

            self.thread.start()



            self.tg_thread = threading.Thread(target=self._telegram_bot_loop, daemon=True)

            self.tg_thread.start()



            logging.info("Box UPS driver poll thread and Telegram bot started.")



    def stop(self):

        self.running = False

        if self.fd is not None:

            try: os.close(self.fd)

            except Exception: pass

            self.fd = None



    def _poll_loop(self):

        while self.running:

            t0 = time.monotonic()

            data, err = self._query_q1()

            now = datetime.now()

            now_str = now.strftime("%Y-%m-%d %H:%M:%S")

            time_short = now.strftime("%H:%M:%S")



            with self.lock:

                self._seq += 1

                if data:

                    self.current_status.update({

                        "connected": True,

                        "timestamp": now_str,

                        "time_short": time_short,

                        "seq": self._seq,

                        **data

                    })



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

                            self.events.appendleft({

                                "timestamp": now_str,

                                "time_short": time_short,

                                "mode": data["mode_title"],

                                "in_v": data["in_v"],

                                "out_v": data["out_v"],

                                "load_pct": data["load_pct"],

                                "batt_v": data["batt_v"]

                            })

                            self._append_csv(data)

                            logging.info(f"STATUS CHANGE: {self.last_mode_code} -> {mode_code}")



                            # Dedicated Telegram Alerts for Power Events

                            if mode_code in ("BATTERY", "BATT_LOW"):

                                self.send_telegram(

                                    f"🚨 <b>Внимание: СВЕТ ОТКЛЮЧЕН!</b>\n\n"

                                    f"🔋 ИБП перешел на работу от аккумулятора\n"

                                    f"⚡ Напряжение сети: <b>0.0 В</b>\n"

                                    f"🔌 Выход на устройства: {data['out_v']} В\n"

                                    f"📊 Заряд АКБ: <b>{data['batt_pct']}%</b> ({data['batt_v']} В)\n"

                                    f"💡 Нагрузка: {data['load_pct']}% (~{data['load_watts']} Вт)\n"

                                    f"🕒 Время: {time_short}"

                                )

                            elif self.last_mode_code in ("BATTERY", "BATT_LOW") and mode_code == "ONLINE":

                                self.send_telegram(

                                    f"✅ <b>СВЕТ ВКЛЮЧЕН!</b>\n\n"

                                    f"🔌 Питание в сети восстановлено: <b>{data['in_v']} В</b>\n"

                                    f"🔋 Заряд аккумулятора: {data['batt_pct']}%\n"

                                    f"🕒 Время: {time_short}"

                                )

                            elif mode_code == "AVR_BOOST":

                                self.send_telegram(

                                    f"⚠️ <b>Просадка напряжения в розетке!</b>\n\n"

                                    f"📉 Входная сеть: <b>{data['in_v']} В</b> (норма 220–230 В)\n"

                                    f"⚡ Стабилизатор AVR вытягивает выход до: <b>{data['out_v']} В</b>\n"

                                    f"🕒 Время: {time_short}"

                                )



                        self.last_mode_code = mode_code



                else:

                    self.current_status.update({

                        "connected": False,

                        "timestamp": now_str,

                        "time_short": time_short,

                        "seq": self._seq,

                        "mode_code": "DISCONNECTED",

                        "mode_title": "Connecting...",

                        "mode_title_ru": "Подключение...",

                        "mode_desc": err or "Waiting for UPS",

                        "mode_desc_ru": err or "Ожидание связи с ИБП",

                        "status_color": "#ef4444"

                    })



                # Energy calculations

                now_mono = time.monotonic()

                dt = now_mono - self.last_poll_time

                self.last_poll_time = now_mono

                load_w = float(self.current_status.get("load_watts", 0)) if self.current_status.get("connected") else 0.0

                total_w = load_w + 15.0

                if self.current_status.get("connected") and 0 < dt < 10.0:

                    self.accumulated_kwh += (total_w * dt) / 3600000.0



                cost_hr = (total_w / 1000.0) * 1.94

                self.energy_status = {

                    "load_watts": round(load_w, 1),

                    "self_watts": 15.0,

                    "total_watts": round(total_w, 1),

                    "tariff": 1.94,

                    "cost_per_hour": round(cost_hr, 2),

                    "cost_per_day": round(cost_hr * 24.0, 2),

                    "cost_per_month": round(cost_hr * 24.0 * 30.0, 2),

                    "accumulated_kwh": round(self.accumulated_kwh, 4),

                    "accumulated_cost": round(self.accumulated_kwh * 1.94, 2)

                }



            elapsed = time.monotonic() - t0

            time.sleep(max(0.1, 1.0 - elapsed))



    def _append_csv(self, data):

        try:

            with open(self.log_file, "a", newline="", encoding="utf-8") as f:

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

            logging.error(f"Error appending CSV: {e}")



    def get_snapshot(self):

        with self.lock:

            return {

                "status": dict(self.current_status),

                "history": list(self.history),

                "events": list(self.events),

                "energy": dict(self.energy_status),

                "shutdown": {

                    "is_counting_down": False,

                    "seconds_left": 0,

                    "warning_type": None,

                    "battery_low": self.current_status.get("is_batt_low", False),

                    "settings": {

                        "battery_shutdown_delay_sec": 300,

                        "shutdown_action": "hibernate",

                        "ups_model_name": "ExeGate SpecialPro UNB-1200",

                        "ups_rated_watts": 750,

                        "electricity_tariff": 1.94,

                        "language": "ru"

                    }

                }

            }