import hid
import time
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config import VENDOR_ID, PRODUCT_ID


def read_megatec():
    print(f"Connecting to UPS {hex(VENDOR_ID)}:{hex(PRODUCT_ID)}...")
    d = hid.device()
    try:
        d.open(VENDOR_ID, PRODUCT_ID)
    except Exception as e:
        print(f"Failed to open device: {e}")
        return

    print("Successfully connected!")
    
    cmd = b'Q1\r'
    payload = cmd.ljust(8, b'\x00')
    write_buf = b'\x00' + payload
    print(f"Sending write_buf: {write_buf}")
    
    written = d.write(write_buf)
    print(f"Bytes written: {written}")

    full_response = b''
    start_time = time.time()
    
    while time.time() - start_time < 2.0:
        data = d.read(64, timeout_ms=500)
        if data:
            chunk = bytes(data)
            full_response += chunk
            print(f"Read chunk ({len(chunk)} bytes): {chunk}")
            if b'\r' in chunk:
                break
        time.sleep(0.05)

    print("\n--- Summary ---")
    print(f"Raw received ({len(full_response)} bytes): {full_response}")
    try:
        text = full_response.decode('ascii', errors='replace').strip()
        print(f"Text output: '{text}'")
    except Exception as e:
        print(f"Decode error: {e}")

    d.close()


if __name__ == "__main__":
    read_megatec()
