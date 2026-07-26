"""Global configuration constants for UPS Monitor."""

import os

# USB HID Vendor ID & Product ID (ExeGate / RichComm Megatec F protocol)
VENDOR_ID = 0x0665
PRODUCT_ID = 0x5161

# Network & Server defaults
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

# File paths & limits
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(PROJECT_ROOT, "ups_power_events.csv")
MAX_HISTORY_POINTS = 120
MAX_EVENTS = 100
POLL_INTERVAL_SEC = 1.0  # Polling rate for USB HID
