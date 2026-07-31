"""Native Windows Sound Manager using winsound."""

import sys
import threading
import logging

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


def _play_beeps(sound_type: str):
    if not HAS_WINSOUND or sys.platform != "win32":
        return

    try:
        if sound_type == "battery":
            # High-pitched emergency alert (880Hz -> 659Hz)
            winsound.Beep(880, 250)
            winsound.Beep(659, 350)
        elif sound_type == "avr":
            # Medium alert (587Hz -> 659Hz)
            winsound.Beep(587, 180)
            winsound.Beep(659, 180)
        elif sound_type == "online":
            # Ascending grid restored chime (523Hz -> 659Hz -> 784Hz)
            winsound.Beep(523, 120)
            winsound.Beep(659, 120)
            winsound.Beep(784, 180)
        elif sound_type == "test":
            # Clear test chime (659Hz -> 880Hz)
            winsound.Beep(659, 150)
            winsound.Beep(880, 250)
        else:
            winsound.Beep(784, 200)
    except Exception as e:
        logging.debug(f"winsound error: {e}")


def play_sound(sound_type: str = "test") -> None:
    """Play a native Windows beep sound asynchronously in a background thread."""
    threading.Thread(target=_play_beeps, args=(sound_type,), daemon=True).start()
