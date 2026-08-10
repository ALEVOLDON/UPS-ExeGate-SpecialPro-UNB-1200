# ExeGate SpecialPro UNB-1200 — Мониторинг ИБП (UPS Monitor)

<p align="center">
  <b>Язык / Language:</b> 
  <a href="README.md">English</a> | <b>Русский</b>
</p>

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-41B883?style=for-the-badge&logo=websocket&logoColor=white)](#)
[![Windows Tray](https://img.shields.io/badge/Windows-System_Tray-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

Современное веб- и десктоп-приложение для мониторинга состояния ИБП **ExeGate SpecialPro UNB-1200** (и совместимых устройств на протоколе RichComm / Megatec `F` через USB HID) с поддержкой **двух языков (английский и русский)**, **безопасного автовыключения Windows** и **системного трея**.

<p align="center">
  <img src="assets/dashboard_preview.jpg" alt="Dashboard Preview" width="100%" style="border-radius: 12px;" />
</p>

<p align="center">
  <img src="assets/modal_preview.jpg" alt="Event Log Modal Window" width="100%" style="border-radius: 12px;" />
</p>

---

## ✨ Основные возможности

- 💡 **Энергопотребление и калькулятор расходов**: Расчет суммарной мощности из розетки ($P_{\text{приборы}} + P_{\text{собственное\_ИБП}}$), стоимости электроэнергии в час, в сутки и прогноза на месяц по настраиваемому тарифу (руб/кВт⋅ч).
- 🔋 **Счетчик кВт⋅ч и затрат за сессию**: Накопительный учет израсходованного электричества и денег с возможностью сброса счетчика в 1 клик.
- 🛡️ **Защита телеметрии от задержек USB (Grace Period)**: 4-секундный буфер удержания данных (бейдж `FROZEN`), исключающий сброс показаний в ноль при микрозадержках опроса USB HID.
- 🌐 **Двуязычный интерфейс (EN / RU)**: Полноценная локализация с мгновенным переключением языка по кнопке в шапке и сохранением настроек.
- ⚡ **Мониторинг в реальном времени**: Отображение входного/выходного напряжения, частоты сети, температуры, нагрузки (%) и мощности (Вт).
- 🛑 **Автовыключение Windows (Graceful Shutdown)**: Автоматическое безопасное завершение работы ПК (`shutdown.exe`) при разряде АКБ ниже настроенного порога с таймером отсчета и отменой в 1 клик.
- 🖥️ **Системный трей Windows**: Иконка в трее с живым статусом питания, всплывающими подсказками и быстрым меню управления.
- 💬 **Нативные уведомления Windows Toast**: Всплывающие системные карточки Windows при сменах режимов (Сеть / AVR / Батарея).
- 🔌 **Интерактивная карта 4 розеток 220V**: Визуализация подключений Schuko 220V с персональными названиями приборов (ПК, Монитор, Роутер) и памятью.
- 🎯 **Дольчатые круговые индикаторы**: Сегментированные радиальные шкалы (20 долек) с градиентной неоновой подсветкой.
- 🔋 **Оценка заряда АКБ**: Интеллектуальный расчёт уровня заряда аккумулятора по кривым напряжения с учётом текущего режима работы.
- 🔄 **Интерактивная схема питания**: Визуализация потоков энергии (Сеть $\rightarrow$ ИБП $\rightarrow$ Нагрузка / Батарея) с анимацией импульсов тока.
- 📊 **Живой график напряжений**: Встроенный график входного и выходного напряжения на основе `Chart.js`.
- 🔔 **Звуковые и Push-уведомления**: Двухуровневые звуковые оповещения и поддержка браузерных уведомлений.
- 📜 **Журнал событий и экспорт CSV**: Автоматическая фиксация событий переключения режимов с возможностью экспорта в CSV в 1 клик и динамическим переводом старых логов.
- 💻 **Десктопный и веб-режим**: Запуск в окне Windows (через `pywebview` + `pystray`) или веб-сервера.

---

## 🛠️ Архитектура проекта

```text
UPS ExeGate SpecialPro UNB-1200/
├── app/
│   ├── config.py           # Централизованные константы и параметры
│   ├── netutil.py          # Сетевые утилиты и проверка портов
│   ├── notifications.py    # Нативные системные уведомления Windows Toast
│   ├── protocol.py         # Парсер протокола Megatec F и очистка сырых кадров
│   ├── server.py           # FastAPI веб-сервер, REST API и WebSockets
│   ├── shutdown_manager.py # Менеджер безопасного завершения работы Windows
│   ├── sound_manager.py    # Асинхронный звуковой движок для Windows
│   ├── tray_icon.py        # Иконка в системном трее Windows (pystray)
│   ├── ups_driver.py       # Фоновый опрос USB HID устройства и трекинг
│   └── static/             # Веб-интерфейс (translations.js, app.js, styles.css)
├── tools/                  # Диагностика и утилиты тестирования USB
├── desktop_app.py          # Десктопная версия (pywebview + tray)
├── main.py                 # Консольный веб-сервер (uvicorn)
├── Run_UPS_Monitor.bat     # Быстрый запуск
├── Run_UPS_Monitor.vbs     # Тихий запуск (без окна консоли)
├── create_shortcut.ps1     # Скрипт создания ярлыка на Рабочем столе
└── requirements.txt        # Зависимости Python (pystray, Pillow, pywebview и др.)
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
