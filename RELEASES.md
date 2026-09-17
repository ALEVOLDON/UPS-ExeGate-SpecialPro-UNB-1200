# GitHub Release Notes — ExeGate SpecialPro UNB-1200 UPS Monitor

This document contains formatted release notes in **English** for GitHub Releases.

---

## 🔌 Release v1.5.0 — Multi-Model UPS Support (SpecialPro Smart LLB-2200 & More)

### ⚙️ Multi-Model Presets & Dynamic Load Rating
- **Model Presets**: Added built-in presets for **ExeGate SpecialPro Smart LLB-2200 (1200 W)**, **UNB-1200 (750 W)**, **UNB-600 (360 W)**, **UNB-800 (480 W)**, **UNB-1500 (900 W)**, **LLB-3000 (1800 W)**, and **Custom UPS**.
- **Active Wattage Scaling**: Active wattage calculations now dynamically scale based on configured model rating rather than hardcoded 750W.
- **Dynamic UI Indicators**: Load gauge caption (`1200 W max`), sidebar badges, and Power Flow diagram automatically reflect the active model in real time.

### 🔋 Intelligent Multi-Battery Auto-Detection
- **Auto-Detection (12V / 24V / 48V)**: Automatically detects 24V battery banks (e.g. LLB-2200 dual-battery setup) and 48V banks, normalizing voltage curves to ensure 100% accurate battery percentage display across all models.
- **Manual Mode Option**: Allows explicit selection of 12V, 24V, 36V, or 48V battery systems.

### 🖥️ Enhanced System Tray & USB Connection
- **Dynamic Tray Tooltip**: System tray icon tooltip now shows the active UPS model name (e.g., `ExeGate LLB-2200: ONLINE`).
- **Resilient USB HID Detection**: Added automatic fallback to alternative Megatec VID/PID pairs.

---

## 📊 Release v1.4.0 — Power Grid Historical Analytics, Incident Diagrams & Protocol Fix

### 📈 Historical Analytics & Stability Dashboard
- **Interactive Period Selector**: Instant statistics filtering for **24 Hours**, **7 Days (Week)**, **30 Days (Month)**, and **All Time** powered by a new high-performance `/api/analytics` backend engine.
- **4 Key Performance Indicator (KPI) Cards**:
  - 🔋 **Time on Battery & Blackout Count**: Accurate sum of runtime on backup battery power with total incident counts.
  - ⚡ **Grid Stability Index**: Dynamic power grid reliability score (e.g. $99.97\%$).
  - 🔄 **AVR Activations**: Total voltage stabilization interventions (Boost & Trim counts).
  - 📉 **Mains Voltage Extremes**: Real-time calculated Minimum, Average, and Maximum recorded grid input voltages.

### 🎨 Visual Incident Diagrams (`Chart.js`)
- **Daily Events & Incidents Timeline**: Stacked bar chart visualizing daily blackout outages vs AVR voltage stabilizations across the selected timeframe.
- **Operating Modes Ratio**: Sleek glowing doughnut chart presenting the percentage breakdown of power conditions (Normal Grid vs AVR vs Battery).
- **Peak Disturbance Hours (00:00 — 23:00)**: 24-hour histogram mapping out the exact times of day when voltage sags, surges, and blackouts most frequently occur.

### 🛠️ Megatec Protocol Parser Fix
- **Status Bit Disambiguation**: Resolved a bug in `protocol.py` where bit 4 (device type: Line-Interactive) was incorrectly flagged as permanent AVR Boost.
- **Accurate State Tracking**: Restored transitions between `ONLINE` (normal grid pass-through), `AVR BOOST`, `AVR TRIM`, and `BATTERY`.
- **Event Log Consistency**: All intermediate voltage stabilization events and returns to normal voltage are now recorded in `ups_power_events.csv`.

---

## ⚡ Release v1.3.0 — Energy Consumption & Electricity Cost Calculator

### 💡 Energy Metering & Real-Time Cost Estimator
- **Grid Power Calculation**: Calculates total power draw from the wall outlet (P_total = P_connected_devices + P_ups_internal) combining active device load and UPS self-consumption.
- **Real-Time Cost Rates**: Real-time calculation of electricity expenses: **Cost per Hour**, **Cost per 24h**, and **Projected Monthly Cost** based on custom tariff rates.
- **Session Energy Tracker**: Millisecond-accurate accumulated energy consumption counter (kWh) and total session cost (руб) with 1-click counter reset.
- **Flexible Settings Integration**: Added input fields in Settings view for electricity tariff rate (руб/kWh) and UPS internal self-consumption (Watts), automatically persisted in `app_settings.json`.

### 🛡️ Telemetry Resilience & Grace Period
- **USB Connection Grace Period**: Implemented a 4-second telemetry hold buffer (`FROZEN` indicator) that prevents screen flickering or zeroing of metrics during temporary USB HID Cypress UART polling delays.
- **Sub-Precision Smooth Animation**: Optimized DOM gauge animations to update sub-precision energy values directly without triggering unnecessary 60 FPS animation loop restarts.

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
