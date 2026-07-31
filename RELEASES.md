# GitHub Release Notes — ExeGate SpecialPro UNB-1200 UPS Monitor

This document contains formatted release notes in **English** for GitHub Releases.

---

## 🚀 Release v1.2.0 — Dual-Language Support (EN/RU) & Sound Engine

### 🌐 Dual-Language Support (i18n)
- **Primary Language**: English is now the default language across the UI, documentation, system tray, and notifications.
- **Language Switcher**: Added a real-time `🌐 EN / RU` toggle button in the top header bar for instant switching between English and Russian without page reload.
- **Settings Persistence**: Language preference is saved in browser `localStorage` and synced with backend `app_settings.json`.
- **Dynamic Event Log Translation**: Historical log entries loaded from `ups_power_events.csv` are automatically translated into the active language on the fly.

### 🔊 Sound Engine & Audio Enhancements
- **Dual-Layer Audio Engine**: Combines Web Audio API (browser) with native Windows hardware speaker alerts via Python `winsound`.
- **Web Audio API Auto-Resume**: Automatic unlocking of Web Audio `AudioContext` on first user interaction to ensure smooth audio alerts across all browsers and pywebview desktop windows.
- **Sound Signal Test Button**: Added a dedicated **"🔊 Test Sound"** button in the Settings tab to test audio signals immediately.

### 💬 Windows Toast Notifications
- **Fixed Toast Notification Dispatch**: Resolved Windows `Shell_NotifyIconW` thread failures by implementing reliable Windows NotifyIcon dispatch.
- **Seamless Toggle**: Merged header Alerts button and Settings toggle to control Windows native toast notifications without popup permission dialogs.

---

## 📦 Release v1.1.0 — Graceful Shutdown, System Tray & Segmented Gauges UI

### 🛑 Graceful Windows Auto-Shutdown
- **Automatic PC Shutdown**: Automatic safe Windows shutdown (`shutdown.exe`) when battery drops below configured threshold (default 15%).
- **Countdown Banner**: Emergency banner with live countdown timer and 1-click cancel button.

### 🖥️ Windows System Tray & Native UI
- **Tray Icon**: Live status glow indicator in Windows system tray with context control menu (`pystray` + `Pillow`).
- **4× 220V Outlets Map**: Interactive Schuko socket map with customizable device labels (PC, Monitor, Router) and memory.
- **Segmented Radial Gauges**: 20-segment arc scales with neon gradient styling.

---

## ⚡ Release v1.0.0 — Initial Release

- **Real-Time Monitoring**: Real-time USB HID telemetry for Megatec F protocol (`0x0665:0x5161`).
- **Live Power Flow Diagram**: Visual energy distribution scheme with pulse animations.
- **Live Charts**: Real-time voltage graphs powered by `Chart.js`.
- **CSV Logging**: Automatic logging of power events to `ups_power_events.csv`.
- **Desktop & Web Modes**: Launchable via `pywebview` desktop window or `uvicorn` web server.
