import hid
import time
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config import VENDOR_ID, PRODUCT_ID


def probe():
    print("Opening USB HID 0665:5161...")
    try:
        d = hid.device()
        d.open(VENDOR_ID, PRODUCT_ID)
    except Exception as e:
        print(f"Error opening device: {e}")
        return

    print("Device opened successfully!")

    print("\n--- Test 1: Passive reading (3 seconds) ---")
    d.set_nonblocking(True)
    t0 = time.time()
    count = 0
    while time.time() - t0 < 3.0:
        data = d.read(64)
        if data:
            print(f"Received passive data ({len(data)} bytes): {bytes(data)}")
            count += 1
        time.sleep(0.1)
    if count == 0:
        print("No passive reports received.")

    d.set_nonblocking(False)
    commands = [b'Q1\r', b'I\r', b'F\r', b'QS\r', b'Q\r', b'P\r', b'Y\r']

    for cmd in commands:
        print(f"\n--- Testing Command: {cmd} ---")
        
        buf_a = b'\x00' + cmd.ljust(8, b'\x00')
        print(f"A) write(b'\\x00' + {cmd}): ", end="")
        try:
            w = d.write(buf_a)
            print(f"written {w}")
            time.sleep(0.15)
            r = d.read(64, timeout_ms=500)
            print(f"   Read response: {bytes(r)}")
        except Exception as e:
            print(f"   Error: {e}")

        buf_b = b'\x00' + cmd
        print(f"B) write(b'\\x00' + {cmd}): ", end="")
        try:
            w = d.write(buf_b)
            print(f"written {w}")
            time.sleep(0.15)
            r = d.read(64, timeout_ms=500)
            print(f"   Read response: {bytes(r)}")
        except Exception as e:
            print(f"   Error: {e}")

        buf_c = b'\x00' + cmd.ljust(8, b'\x00')
        print(f"C) send_feature_report({cmd}): ", end="")
        try:
            w = d.send_feature_report(buf_c)
            print(f"sent {w}")
            time.sleep(0.15)
            feat = d.get_feature_report(0, 64)
            print(f"   Get feature report: {bytes(feat)}")
        except Exception as e:
            print(f"   Error: {e}")

    d.close()


if __name__ == "__main__":
    probe()
