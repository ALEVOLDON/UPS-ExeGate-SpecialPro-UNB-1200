import hid
import time
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config import VENDOR_ID, PRODUCT_ID


def scan_device():
    d = hid.device()
    d.open(VENDOR_ID, PRODUCT_ID)
    
    print("Probing HID write / feature report mechanisms...")

    cmd = b'Q1\r'
    
    for r_id in range(0, 5):
        print(f"\n--- Testing Report ID {r_id} ---")
        try:
            buf = bytes([r_id]) + cmd.ljust(8, b'\x00')
            w = d.write(buf)
            print(f"Write ID {r_id}: returned {w}")
            time.sleep(0.1)
            res = d.read(64, timeout_ms=300)
            print(f"Read after write ID {r_id}: {bytes(res)}")
        except Exception as e:
            print(f"Write ID {r_id} failed: {e}")

        try:
            buf = bytes([r_id]) + cmd.ljust(8, b'\x00')
            f_send = d.send_feature_report(buf)
            print(f"send_feature_report ID {r_id}: returned {f_send}")
            time.sleep(0.1)
            f_get = d.get_feature_report(r_id, 65)
            print(f"get_feature_report ID {r_id}: returned {bytes(f_get)}")
        except Exception as e:
            print(f"feature report ID {r_id} failed: {e}")

    d.close()


if __name__ == "__main__":
    scan_device()
