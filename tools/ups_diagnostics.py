"""UPS Diagnostic Utility for ExeGate SpecialPro UNB-1200."""

import hid
import time
import sys
import os
import csv
from datetime import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.config import VENDOR_ID, PRODUCT_ID, LOG_FILE
from app.protocol import parse_f_response


class UPSCommunicator:
    def __init__(self):
        self.dev = None

    def connect(self):
        try:
            self.dev = hid.device()
            self.dev.open(VENDOR_ID, PRODUCT_ID)
            return True
        except Exception:
            self.dev = None
            return False

    def close(self):
        if self.dev:
            try:
                self.dev.close()
            except Exception:
                pass
            self.dev = None

    def query(self):
        if not self.dev:
            if not self.connect():
                return None, "Device not found on USB HID"

        try:
            cmd = b'F\r'.ljust(8, b'\x00')
            self.dev.write(b'\x00' + cmd)
        except Exception as e:
            self.close()
            return None, f"USB write error: {e}"

        time.sleep(0.1)
        full_res = b""
        start_t = time.time()
        
        while time.time() - start_t < 0.8:
            try:
                buf = self.dev.read(64, timeout_ms=200)
                if buf:
                    full_res += bytes(buf)
                    if b'\r' in full_res:
                        break
            except Exception:
                break
            time.sleep(0.05)

        if not full_res:
            return None, "No response to F command"

        try:
            text = full_res.decode('ascii', errors='ignore')
            parsed = parse_f_response(text)
            if parsed:
                return parsed, None
            else:
                return None, f"Unrecognized response: '{text.strip()}'"
        except Exception as e:
            return None, f"Decode error: {e}"


def init_csv():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Mode", "Input_Voltage_V", "Output_Voltage_V", "Load_Percent", "Battery_Voltage_V", "Temperature_C", "Raw_Status"])


def log_event(data):
    init_csv()
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("mode_title", "UNKNOWN"),
            data["in_v"],
            data["out_v"],
            data["load_pct"],
            data["batt_v"],
            data["temp"],
            data["status_bits"]
        ])


def main():
    print("=" * 65)
    print(" UPS DIAGNOSTIC UTILITY - ExeGate SpecialPro UNB-1200")
    print("=" * 65)
    print(f" Saving events log to: {LOG_FILE}\n")

    ups = UPSCommunicator()
    init_csv()

    last_mode = None

    try:
        while True:
            data, err = ups.query()
            now_str = datetime.now().strftime("%H:%M:%S")

            if err:
                print(f"\n[{now_str}] WARNING: {err}")
                time.sleep(2)
                continue

            mode_title = data.get("mode_title", "UNKNOWN")
            if mode_title != last_mode:
                if last_mode is not None:
                    print(f"\n[{now_str}] MODE CHANGE: {last_mode}  ===>  {mode_title} (In: {data['in_v']}V -> Out: {data['out_v']}V)")
                log_event(data)
                last_mode = mode_title

            status_line = (
                f"\r[{now_str}] Mains: {data['in_v']:5.1f}V | "
                f"Output: {data['out_v']:5.1f}V | "
                f"Load: {data['load_pct']:2d}% | "
                f"Batt: {data['batt_v']:4.1f}V | "
                f"Mode: {mode_title:<20}"
            )
            sys.stdout.write(status_line)
            sys.stdout.flush()

            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nDiagnostic stopped.")
    finally:
        ups.close()


if __name__ == "__main__":
    main()
