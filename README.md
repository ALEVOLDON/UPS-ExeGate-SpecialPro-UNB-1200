# ExeGate SpecialPro UNB-1200 — UPS Monitor

<p align="center">
  <b>Language / Язык:</b> 
  <b>English</b> | <a href="README_RU.md">Русский</a>
</p>

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-41B883?style=for-the-badge&logo=websocket&logoColor=white)](#)
[![Windows Tray](https://img.shields.io/badge/Windows-System_Tray-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

A modern web and desktop monitoring application for **ExeGate SpecialPro UNB-1200** (and compatible RichComm / Megatec `F` protocol devices over USB HID) featuring **graceful Windows auto-shutdown**, **system tray icon**, **dual-language UI (English & Russian)**, and **real-time power telemetry**.

<p align="center">
  <img src="assets/dashboard_preview.jpg" alt="Dashboard Preview" width="100%" style="border-radius: 12px;" />
</p>

<p align="center">
  <img src="assets/modal_preview.jpg" alt="Event Log Modal Window" width="100%" style="border-radius: 12px;" />
</p>

---

## ✨ Features

- 🌐 **Dual-Language Support (EN / RU)**: Full internationalization with real-time language switching button and persistent language settings.
- ⚡ **Real-Time Telemetry**: Live monitoring of Input/Output voltage, grid frequency, internal temperature, load percentage (%), and power consumption (Watts).
- 🛑 **Graceful Windows Auto-Shutdown**: Automatic safe PC shutdown (`shutdown.exe`) when battery drops below threshold, with countdown timer and 1-click cancel button.
- 🖥️ **Windows System Tray**: Tray icon with live color status glow, tooltips, and context control menu.
- 💬 **Windows Native Toast Notifications**: Pop-up OS notifications for power mode transitions (Mains / AVR / Battery).
- 🔌 **Interactive 4× 220V Outlets Map**: Visual map for 4× Schuko CEE 7/4 sockets with customizable device labels (PC, Monitor, Router) and memory.
- 🎯 **Segmented Radial Gauges**: 20-segment arc scales with neon gradient styling.
- 🔋 **Smart Battery Percentage Calculation**: Intelligent battery level estimation based on voltage discharge curves and operating mode.
- 🔄 **Interactive Power Flow Diagram**: Dynamic energy flow scheme (Mains $\rightarrow$ UPS $\rightarrow$ Load / Battery) with animated current pulse indicators.
- 📊 **Live Voltage Charting**: Built-in real-time Input vs Output voltage trend graphs using `Chart.js`.
- 🔔 **Audio & Push Alerts**: Dual-layer sound chime alerts and browser push support.
- 📜 **Event Logging & CSV Export**: Automatic recording of power events with 1-click CSV file export and dynamic historical log translation.
- 💻 **Desktop & Web Modes**: Launch as a native Windows desktop app (`pywebview` + `pystray`) or a standalone Web Server.

---

## 🛠️ Project Structure

```text
UPS ExeGate SpecialPro UNB-1200/
├── app/
│   ├── config.py           # Centralized configuration & constants
│   ├── netutil.py          # Network utilities & port checker
│   ├── notifications.py    # Native Windows Toast notifications
│   ├── protocol.py         # Megatec F protocol parser & data cleaner
│   ├── server.py           # FastAPI web server, REST API & WebSockets
│   ├── shutdown_manager.py # Windows graceful shutdown manager
│   ├── sound_manager.py    # Async native Windows sound alert player
│   ├── tray_icon.py        # Windows system tray icon (pystray)
│   ├── ups_driver.py       # USB HID background polling thread & state tracking
│   └── static/             # Web UI assets (translations.js, app.js, styles.css)
├── tools/                  # USB HID diagnostic scripts & protocol tests
├── desktop_app.py          # Native desktop application (pywebview + tray)
├── main.py                 # Standalone web server launcher (uvicorn)
├── Run_UPS_Monitor.bat     # Quick launcher batch script
├── Run_UPS_Monitor.vbs     # Silent background launcher (no console window)
├── create_shortcut.ps1     # PowerShell script to generate Desktop shortcut
└── requirements.txt        # Python dependencies (pystray, Pillow, pywebview, etc.)
```

---

## 🚀 Quick Start

### 1. Install Dependencies
Ensure **Python 3.9+** is installed on your system.

```bash
pip install -r requirements.txt
```

### 2. Run the Application

#### Option A: Desktop Window (Recommended)
Double-click `Run_UPS_Monitor.vbs` (runs silently without a console window) or launch via command line:

```bash
python desktop_app.py
```

#### Option B: Standalone Web Server
```bash
python main.py
```
Open your browser at `http://127.0.0.1:8000`

---

## 📌 Desktop Shortcut Creation

To create a shortcut on your Windows Desktop:

```powershell
powershell -ExecutionPolicy Bypass -File .\create_shortcut.ps1
```

---

## 🔌 Technical Protocol Details

- **Vendor ID**: `0x0665`
- **Product ID**: `0x5161`
- **Protocol**: RichComm / Megatec (Command `F\r`)
- **Response Format**: `F(MMM.M NNN.N PPP.P QQQ RR.R S.SS TT.T b7b6b5b4b3b2b1b0`

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
