import sys
import time
import os
from datetime import datetime
import hid

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.config import VENDOR_ID, PRODUCT_ID


def main():
    print("=" * 64)
    print(" TEST: сырые кадры USB при отключении сети")
    print(" Закройте UPS Monitor / desktop_app перед запуском!")
    print(" Вытащите вилку ИБП ИЗ СТЕНЫ и смотрите, меняется ли F(...)")
    print(" Ctrl+C — выход. Лог также: unplug_test_log.txt")
    print("=" * 64)

    d = hid.device()
    d.open(VENDOR_ID, PRODUCT_ID)
    d.set_nonblocking(True)

    prev = None
    changes = 0
    n = 0
    log_path = os.path.join(PROJECT_ROOT, "unplug_test_log.txt")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n--- session {datetime.now().isoformat()} ---\n")
        try:
            while True:
                for _ in range(16):
                    if not d.read(64):
                        break
                body = b"F\r".ljust(8, b"\x00")
                out = bytes([0x00]) + body + bytes(64 - len(body))
                d.write(out)
                time.sleep(0.08)
                full = b""
                t0 = time.time()
                while time.time() - t0 < 0.5:
                    b = d.read(64)
                    if b:
                        full += bytes(b)
                        if b"\r" in full:
                            break
                    time.sleep(0.01)

                frame = full.split(b"\r")[0].decode("ascii", "replace") if full else "<empty>"
                frame = "".join(ch for ch in frame if ch.isprintable())
                n += 1
                ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                mark = ""
                if prev is not None and frame != prev:
                    changes += 1
                    mark = " <<< CHANGE"
                    print(f"\n*** КАДР ИЗМЕНИЛСЯ #{changes} ***")
                line = f"[{ts}] #{n} {frame}{mark}"
                print(line)
                log.write(line + "\n")
                log.flush()
                prev = frame
                time.sleep(0.4)
        except KeyboardInterrupt:
            print(f"\nСтоп. Всего кадров: {n}, изменений: {changes}")
            print(f"Лог: {log_path}")
            if changes == 0:
                print(
                    "\nВЫВОД: USB ни разу не изменил ответ.\n"
                    "Программа не может увидеть батарею — ИБП/мост не шлёт live-статус.\n"
                    "Проверьте то же в PowerManager II: если там тоже не меняется — железо/прошивка."
                )
        finally:
            d.close()


if __name__ == "__main__":
    main()
