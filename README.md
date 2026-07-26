# ExeGate SpecialPro UNB-1200 — Мониторинг ИБП (UPS Monitor)

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-41B883?style=for-the-badge&logo=websocket&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

Современное веб- и десктоп-приложение для мониторинга состояния ИБП **ExeGate SpecialPro UNB-1200** (и совместимых устройств на протоколе RichComm / Megatec `F` через USB HID).

![Dashboard Preview](app/static/index.html)

---

## ✨ Основные возможности

- ⚡ **Мониторинг в реальном времени**: отображение входного/выходного напряжения, частоты сети, температуры, нагрузки (%) и мощности (Вт).
- 🔋 **Оценка заряда АКБ**: интеллектуальный расчёт уровня заряда аккумулятора по кривым напряжения с учётом текущего режима работы.
- 🔄 **Интерактивная схема питания**: визуализация потоков энергии (Сеть $\rightarrow$ ИБП $\rightarrow$ Нагрузка / Батарея) с анимацией импульсов тока.
- 📊 **Живой график напряжений**: встроенный график входного и выходного напряжения на основе `Chart.js`.
- 🔔 **Звуковые и Push-уведомления**: оповещения при скачках напряжения, сработках AVR и переходе на аккумулятор.
- 📜 **Журнал событий и экспорт CSV**: автоматическая фиксация событий переключения режимов с возможностью экспорта в CSV в 1 клик.
- 💻 **Десктопный и веб-режим**: возможность запуска как автономного приложения в окне Windows (через `pywebview`) или веб-сервера.

---

## 🛠️ Архитектура проекта

```text
UPS ExeGate SpecialPro UNB-1200/
├── app/
│   ├── config.py         # Централизованные константы и параметры
│   ├── netutil.py        # Сетевые утилиты и проверка портов
│   ├── protocol.py       # Парсер протокола Megatec F и логика АКБ
│   ├── server.py         # FastAPI веб-сервер и обработчик WebSockets
│   ├── ups_driver.py     # Фоновый опрос USB HID устройства
│   └── static/           # Интерфейс (HTML, CSS, JS, Chart.js)
├── tools/                # Диагностика и утилиты тестирования USB
├── desktop_app.py        # Десктопная версия (pywebview)
├── main.py               # Консольный веб-сервер (uvicorn)
├── Run_UPS_Monitor.bat   # Быстрый запуск
├── Run_UPS_Monitor.vbs   # Тихий запуск (без окна консоли)
├── create_shortcut.ps1   # Скрипт создания ярлыка на Рабочем столе
└── requirements.txt      # Зависимости Python
```

---

## 🚀 Быстрый запуск

### 1. Установка зависимостей
Убедитесь, что у вас установлен **Python 3.9+**.

```bash
pip install -r requirements.txt
```

### 2. Запуск приложения

#### Вариант А: Десктопное окно (рекомендуется)
Двойной клик по файлу `Run_UPS_Monitor.vbs` (без окна консоли) или через консоль:

```bash
python desktop_app.py
```

#### Вариант Б: Веб-сервер в браузере
```bash
python main.py
```
После запуска откроется веб-интерфейс по адресу: `http://127.0.0.1:8000`

---

## 📌 Создание ярлыка на Рабочем столе

Чтобы создать ярлык приложения на Рабочем столе Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\create_shortcut.ps1
```

---

## 🔌 Технические подробности

- **Vendor ID**: `0x0665`
- **Product ID**: `0x5161`
- **Протокол**: RichComm / Megatec (команда `F\r`)
- **Формат ответа**: `F(MMM.M NNN.N PPP.P QQQ RR.R S.SS TT.T b7b6b5b4b3b2b1b0`

---

## 📄 Лицензия

Проект распространяется под лицензией [MIT](LICENSE).
