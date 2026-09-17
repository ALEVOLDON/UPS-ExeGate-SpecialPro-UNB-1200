const TRANSLATIONS = {
  en: {
    app_title: "ExeGate SpecialPro — UPS Monitor",
    brand_name: "ExeGate Pro",
    brand_sub: "SpecialPro · USB HID",

    // Navigation
    nav_overview: "Overview",
    nav_flow: "Power Flow",
    nav_analytics: "Analytics",
    nav_events: "Event Log",
    nav_settings: "Settings",
    nav_about: "About",

    sidebar_connected: "CONNECTED",
    sidebar_disconnected: "DISCONNECTED",

    // Header Views
    view_dashboard: "Monitoring Dashboard",
    view_flow: "Interactive Power Flow Scheme",
    view_analytics: "Analytics & Voltage Dynamics",
    view_events: "Power Event Log",
    view_settings: "Alerts & System Settings",
    view_about: "About ExeGate Pro",

    // Controls
    sound_toggle: "Sound",
    notif_toggle: "Alerts",
    sound_off: "Muted",
    notif_off: "Off",

    // Emergency Shutdown Banner
    shutdown_alert_title: "CRITICAL BATTERY LEVEL — PC SHUTDOWN INITIATED!",
    shutdown_alert_reason: "Reason: Battery discharged below threshold",
    shutdown_cancel_btn: "Cancel PC Shutdown",

    // Status Banner
    status_connecting: "Connecting...",
    status_init_usb: "Initializing USB connection",

    // Raw Bar
    raw_usb_label: "Raw USB",
    live_data: "LIVE DATA",
    frozen: "FROZEN",
    no_connection: "NO CONNECTION",

    // Gauges
    card_in_v: "Mains Input",
    card_out_v: "UPS Output",
    card_batt: "Battery Charge",
    card_load: "Output Load",
    unit_v: "V",
    unit_hz: "Hz",
    unit_w: "W",
    unit_pct: "%",
    status_grid_ok: "Grid Power OK",
    status_grid_no: "No Grid Power",
    status_batt_mode: "On Battery Power",
    status_normal: "Normal",
    est_by_v: "estimated by V",
    max_w_caption: "750 W max",

    // Mini Stats
    mini_freq: "Frequency",
    mini_temp: "Temperature",
    mini_power: "Power",
    mini_batt_v: "Battery Voltage",
    mini_status_bits: "Status bits",

    // Dashboard sections
    voltage_chart_title: "Voltage Graph",
    voltage_chart_sub: "Input vs Output",
    chart_in_v: "Input (V)",
    chart_out_v: "Output (V)",
    event_log_title: "Event Log",
    btn_expand: "Expand",

    // Tables
    tbl_time: "Time",
    tbl_mode: "Mode",
    tbl_in_v: "Input V",
    tbl_out_v: "Output V",
    tbl_load: "Load",
    tbl_batt_v: "Batt V",
    tbl_time_date: "Time / Date",
    tbl_empty: "Event history is empty",
    tbl_not_found: "No matching events found",
    tbl_loading: "Loading events...",

    // Power Flow
    flow_title: "Interactive Power Distribution Diagram",
    node_mains: "Mains 220V",
    node_ups: "UPS UNB-1200",
    node_batt: "Battery 12V",
    node_load: "Consumers",

    // Socket Outlets Panel
    outlets_title: "220V Outlets Map (4× Schuko CEE 7/4)",
    outlets_sub: "Click outlet label to customize connected device name",
    socket_num_1: "OUTLET № 1",
    socket_num_2: "OUTLET № 2",
    socket_num_3: "OUTLET № 3",
    socket_num_4: "OUTLET № 4",
    socket_placeholder: "Device name...",
    socket_active: "ACTIVE",
    socket_disabled: "DISABLED",
    socket_default_1: "PC Tower",
    socket_default_2: "Monitor",
    socket_default_3: "Wi-Fi Router",
    socket_default_4: "Backup Outlet",

    // Analytics Tab
    an_main_title: "Power Grid & UPS Statistics",
    an_main_sub: "Historical telemetry analysis & stability reports",
    period_24h: "24 Hours",
    period_7d: "7 Days",
    period_30d: "30 Days",
    period_all: "All Time",
    kpi_batt_time: "Time on Battery",
    kpi_outages_lbl: "blackouts",
    kpi_stability: "Grid Stability Index",
    kpi_stability_desc: "Mains power reliability",
    kpi_avr_count: "AVR Activations",
    kpi_voltage_avg: "Avg Input Voltage",
    chart_daily_title: "Daily Events & Incidents Timeline",
    chart_daily_sub: "Blackout outages vs AVR voltage stabilizations",
    chart_modes_title: "Operating Modes Ratio",
    chart_modes_sub: "Percentage breakdown of power conditions",
    chart_hourly_title: "Peak Disturbance Hours (00:00 — 23:00)",
    chart_hourly_sub: "Frequency of power drops and surges by time of day",
    chart_legend_blackout: "Outages (Battery)",
    chart_legend_avr: "AVR Stabilization",
    chart_legend_online: "Normal Grid",
    chart_disturbances_lbl: "Disturbances / Events",
    analytics_title: "Detailed Voltage Dynamics Graph",
    analytics_sub: "Mains Input Voltage vs UPS Output Voltage (Real-Time)",

    // Events Tab & Modal
    events_full_title: "Full Power Event Log",
    search_placeholder: "🔍 Search by date or mode (AVR, Battery)...",

    // Settings Tab
    settings_header_title: "Safe Shutdown & Alert Settings",
    set_auto_shutdown_title: "Windows Graceful Auto Shutdown",
    set_auto_shutdown_desc: "Automatically shuts down PC when battery discharges below threshold",
    set_batt_threshold_title: "Battery Threshold for Shutdown",
    set_batt_threshold_desc: "Battery charge percentage to trigger PC shutdown",
    set_delay_title: "Shutdown Countdown Timer",
    set_delay_desc: "Delay before final PC power off (allows cancellation)",
    set_toast_title: "Windows Native Toast Notifications",
    set_toast_desc: "Pop-up cards in Windows tray area on power events",
    set_test_title: "Test PC Auto Shutdown",
    set_test_desc: "Triggers a 60-second test countdown. Test the cancel button!",
    btn_test_shutdown: "Test (60s)",
    btn_test_sound: "Test Sound",
    set_sound_title: "Audio & Beep Alerts",
    set_sound_desc: "Audio alert when switching to battery or AVR mode",
    set_hw_title: "USB HID Device & System Tray",
    set_hw_desc: "Vendor: 0x0665 · Product: 0x5161 (RichComm Megatec F)",
    tag_active_tray: "Active (Tray)",
    set_csv_title: "Export Event Log Archive",
    set_csv_desc: "Download ups_power_events.csv history file",
    btn_download_csv: "Download CSV",
    btn_enabled: "Enabled",
    btn_disabled: "Disabled",
    sec_unit: "sec",

    // Energy & Cost Calculator
    card_energy_title: "Energy & Electricity Costs",
    card_energy_sub: "Real-Time Power & Cost Estimator",
    energy_total_grid: "Total Grid Draw",
    energy_load_power: "Connected Devices",
    energy_self_power: "UPS Internal Draw",
    energy_cost_hour: "Cost / Hour",
    energy_cost_day: "Cost / 24h",
    energy_cost_month: "Est. / Month",
    energy_session_kwh: "Total Consumed",
    energy_session_cost: "Total Cost",
    btn_reset_energy: "Reset Counter",
    set_tariff_title: "Electricity Tariff (RUB / kWh)",
    set_tariff_desc: "Price per 1 kWh used for cost calculations",
    set_self_watts_title: "UPS Internal Draw (Watts)",
    set_self_watts_desc: "Power consumed by UPS control board & charging circuit",
    set_model_title: "UPS Model & Rated Power",
    set_model_desc: "Select your UPS model or specify custom wattage",
    set_model_custom: "Custom Model...",
    set_rated_watts_title: "Active Rated Power (Watts)",
    set_rated_watts_desc: "Active power capacity used for load percentage calculations",
    set_batt_mode_title: "Battery Voltage System",
    set_batt_mode_desc: "Battery configuration for accurate percentage estimation",
    batt_mode_auto: "Auto-detect (12V / 24V / 48V)",
    batt_mode_12v: "12V (1× 12V Battery)",
    batt_mode_24v: "24V (2× 12V Batteries)",
    batt_mode_36v: "36V (3× 12V Batteries)",
    batt_mode_48v: "48V (4× 12V Batteries)",
    max_w_fmt: "{watts} W max",
    currency_rub: "₽",
    unit_kwh: "kWh",
    rub_per_kwh: "₽/kWh",

    // About Section
    about_app_desc: "Professional Real-Time Telemetry, Safety & Power Analytics for ExeGate SpecialPro Series",
    about_version_label: "Version",
    about_release_label: "Release",
    about_license_label: "License",
    about_author_label: "Author / Developer",
    about_btn_github: "GitHub Repository",
    about_btn_releases: "Releases & Updates",
    about_btn_issues: "Report Issue / Feedback",
    about_feat_telemetry_title: "Real-Time Telemetry & AVR",
    about_feat_telemetry_desc: "Direct USB HID communication via Megatec F protocol with accurate AVR Boost / Trim state tracking and 4-second freeze buffer protection.",
    about_feat_models_title: "Multi-Model & Smart Battery",
    about_feat_models_desc: "Built-in presets for SpecialPro UNB-1200, Smart LLB-2200, UNB-600/800/1500, LLB-3000 and custom models with smart 12V/24V/48V auto-detection.",
    about_feat_shutdown_title: "Graceful Windows Auto-Shutdown",
    about_feat_shutdown_desc: "Configurable automatic shutdown when battery discharges below threshold, with 1-click cancellation, Tray icon and native Toast alerts.",
    about_feat_analytics_title: "Power Grid Analytics & Costs",
    about_feat_analytics_desc: "Historical incident breakdown, grid stability index, peak disturbance hour histogram, and real-time electricity tariff cost tracker.",
    about_hw_title: "Supported Hardware & Architecture",
    about_hw_desc: "ExeGate SpecialPro UNB and Smart LLB series (USB HID 0665:5161). Space-padded frame architecture preventing Cypress UART driver crashes.",

    // Modal
    modal_log_title: "📜 Power Event Log",
    events_count_fmt: "{filtered} of {total} events",

    // Status Modes
    mode_online: "ONLINE",
    mode_online_desc: "Mains power stable. Battery fully charged.",
    mode_battery: "ON BATTERY",
    mode_battery_desc: "Running on internal batteries! Mains power lost.",
    mode_avr_boost: "AVR BOOST",
    mode_avr_boost_desc: "Grid voltage drop ({in_v}V). Boosting output to {out_v}V.",
    mode_avr_trim: "AVR TRIM",
    mode_avr_trim_desc: "High grid voltage ({in_v}V). Trimming output to {out_v}V.",
    mode_avr: "AVR STABILIZATION",
    mode_avr_desc: "Mains voltage stabilization ({in_v}V -> {out_v}V).",
    mode_disconnected: "RECONNECTING...",
    mode_disconnected_desc: "Reconnecting to USB UPS..."
  },

  ru: {
    app_title: "ExeGate SpecialPro — Мониторинг ИБП",
    brand_name: "ExeGate Pro",
    brand_sub: "SpecialPro · USB HID",

    // Navigation
    nav_overview: "Обзор",
    nav_flow: "Схема питания",
    nav_analytics: "Аналитика",
    nav_events: "Журнал",
    nav_settings: "Настройки",
    nav_about: "О программе",

    sidebar_connected: "ПОДКЛЮЧЕНО",
    sidebar_disconnected: "НЕТ СВЯЗИ",

    // Header Views
    view_dashboard: "Дашборд мониторинга",
    view_flow: "Интерактивная схема питания",
    view_analytics: "Аналитика и динамика напряжений",
    view_events: "Журнал событий питания",
    view_settings: "Настройки оповещений и системы",
    view_about: "О программе",

    // Controls
    sound_toggle: "Звук",
    notif_toggle: "Алерты",
    sound_off: "Выкл",
    notif_off: "Выкл",

    // Emergency Shutdown Banner
    shutdown_alert_title: "КРИТИЧЕСКИЙ ЗАРЯД БАТАРЕИ — АВТОВЫКЛЮЧЕНИЕ ПК!",
    shutdown_alert_reason: "Причина: разряд АКБ ниже порога",
    shutdown_cancel_btn: "Отменить выключение ПК",

    // Status Banner
    status_connecting: "Подключение...",
    status_init_usb: "Инициализация USB",

    // Raw Bar
    raw_usb_label: "Сырой USB",
    live_data: "LIVE DATA",
    frozen: "ЗАМОРОЖЕНО",
    no_connection: "НЕТ СВЯЗИ",

    // Gauges
    card_in_v: "Входная сеть",
    card_out_v: "Выход ИБП",
    card_batt: "Заряд АКБ",
    card_load: "Нагрузка",
    unit_v: "В",
    unit_hz: "Гц",
    unit_w: "Вт",
    unit_pct: "%",
    status_grid_ok: "Сеть в норме",
    status_grid_no: "Нет сети",
    status_batt_mode: "Питание от АКБ",
    status_normal: "Норма",
    est_by_v: "оценка по V",
    max_w_caption: "750 Вт max",

    // Mini Stats
    mini_freq: "Частота",
    mini_temp: "Температура",
    mini_power: "Мощность",
    mini_batt_v: "АКБ напряжение",
    mini_status_bits: "Status bits",

    // Dashboard sections
    voltage_chart_title: "График напряжений",
    voltage_chart_sub: "Вход vs Выход",
    chart_in_v: "Вход (В)",
    chart_out_v: "Выход (В)",
    event_log_title: "Журнал событий",
    btn_expand: "Развернуть",

    // Tables
    tbl_time: "Время",
    tbl_mode: "Режим",
    tbl_in_v: "Вход V",
    tbl_out_v: "Выход V",
    tbl_load: "Нагрузка",
    tbl_batt_v: "АКБ V",
    tbl_time_date: "Время / Дата",
    tbl_empty: "История пуста",
    tbl_not_found: "События не найдены",
    tbl_loading: "Загрузка событий...",

    // Power Flow
    flow_title: "Интерактивная схема распределения питания",
    node_mains: "Сеть 220V",
    node_ups: "ИБП UNB-1200",
    node_batt: "АКБ 12V",
    node_load: "Потребители",

    // Socket Outlets Panel
    outlets_title: "Карта подключений розеток 220V (4× Schuko CEE 7/4)",
    outlets_sub: "Кликните на название розетки, чтобы изменить подключенное устройство",
    socket_num_1: "РОЗЕТКА № 1",
    socket_num_2: "РОЗЕТКА № 2",
    socket_num_3: "РОЗЕТКА № 3",
    socket_num_4: "РОЗЕТКА № 4",
    socket_placeholder: "Название устройства...",
    socket_active: "АКТИВНА",
    socket_disabled: "ОТКЛЮЧЕНА",
    socket_default_1: "Системный блок ПК",
    socket_default_2: "Монитор",
    socket_default_3: "Wi-Fi Роутер",
    socket_default_4: "Резервная розетка",

    // Analytics Tab
    an_main_title: "Статистика и аналитика сети / ИБП",
    an_main_sub: "Анализ исторической телеметрии и отчеты стабильности сети",
    period_24h: "24 часа",
    period_7d: "7 дней (Неделя)",
    period_30d: "30 дней (Месяц)",
    period_all: "За всё время",
    kpi_batt_time: "Время работы от АКБ",
    kpi_outages_lbl: "отключений",
    kpi_stability: "Индекс стабильности сети",
    kpi_stability_desc: "Надёжность электроснабжения",
    kpi_avr_count: "Срабатываний AVR",
    kpi_voltage_avg: "Среднее Uвх сети",
    chart_daily_title: "Хронология событий и сбоев по дням",
    chart_daily_sub: "Отключения (АКБ) vs Стабилизация напряжения (AVR)",
    chart_modes_title: "Распределение режимов работы",
    chart_modes_sub: "Процентное соотношение состояний питания",
    chart_hourly_title: "Пиковая активность сбоев по часам суток (00:00 — 23:00)",
    chart_hourly_sub: "Частота просадок и скачков напряжения в разное время суток",
    chart_legend_blackout: "Отключения (АКБ)",
    chart_legend_avr: "Стабилизация AVR",
    chart_legend_online: "Сеть в норме",
    chart_disturbances_lbl: "Сбоев / событий",
    analytics_title: "Детальный график динамики напряжений",
    analytics_sub: "Входное напряжение vs Выходное напряжение ИБП (В реальном времени)",

    // Events Tab & Modal
    events_full_title: "Полный журнал событий питания",
    search_placeholder: "🔍 Быстрый поиск по дате или режиму (AVR, Батарея)...",

    // Settings Tab
    settings_header_title: "Настройки безопасного выключения и оповещений",
    set_auto_shutdown_title: "Автовыключение Windows (Graceful Shutdown)",
    set_auto_shutdown_desc: "Автоматически завершает работу ПК при разряде АКБ ниже порога",
    set_batt_threshold_title: "Порог разряда АКБ для выключения",
    set_batt_threshold_desc: "При каком проценте заряда запускать завершение работы ПК",
    set_delay_title: "Время таймера отсчёта выключения",
    set_delay_desc: "Задержка перед окончательным отключением ПК (для отмены)",
    set_toast_title: "Нативные уведомления Windows (Toast)",
    set_toast_desc: "Всплывающие карточки в углу экрана Windows при событиях сети",
    set_test_title: "Проверка автовыключения ПК",
    set_test_desc: "Запустит тестовый отсчёт 60 секунд. Проверьте кнопку отмены!",
    btn_test_shutdown: "Проверить (60с)",
    btn_test_sound: "Проверить звук",
    set_sound_title: "Звуковые алерты и сигналы ИБП",
    set_sound_desc: "Звуковые сигналы при переходах на АКБ, сработках AVR и восстановлении сети",
    set_hw_title: "USB HID устройство & Трей",
    set_hw_desc: "Vendor: 0x0665 · Product: 0x5161 (RichComm Megatec F)",
    tag_active_tray: "Активен (Трей)",
    set_csv_title: "Выгрузка архива событий",
    set_csv_desc: "Скачать файл истории ups_power_events.csv",
    btn_download_csv: "Скачать CSV",
    btn_enabled: "Включено",
    btn_disabled: "Выключено",
    sec_unit: "сек",

    // Energy & Cost Calculator
    card_energy_title: "Энергопотребление и расходы",
    card_energy_sub: "Расчет мощности сети и стоимости электроэнергии",
    energy_total_grid: "Мощность из сети",
    energy_load_power: "Нагрузка приборов",
    energy_self_power: "Собственное потребление ИБП",
    energy_cost_hour: "Стоимость / час",
    energy_cost_day: "Стоимость / сутки",
    energy_cost_month: "Прогноз / месяц",
    energy_session_kwh: "Израсходовано энергии",
    energy_session_cost: "Суммарная стоимость",
    btn_reset_energy: "Сбросить счетчик",
    set_tariff_title: "Тариф на электроэнергию (руб / кВт⋅ч)",
    set_tariff_desc: "Цена за 1 кВт⋅ч для калькулятора расходов",
    set_self_watts_title: "Собственное потребление ИБП (Вт)",
    set_self_watts_desc: "Мощность платы управления ИБП и схемы зарядки АКБ",
    set_model_title: "Модель ИБП и номинальная мощность",
    set_model_desc: "Выберите модель вашего ИБП или настройте мощность вручную",
    set_model_custom: "Пользовательская модель...",
    set_rated_watts_title: "Номинальная мощность ИБП (Вт)",
    set_rated_watts_desc: "Активная мощность ИБП для точного расчёта нагрузки в Ваттах",
    set_batt_mode_title: "Конфигурация батарейного блока",
    set_batt_mode_desc: "Напряжение АКБ для правильного отображения шкалы заряда",
    batt_mode_auto: "Автоопределение (12V / 24V / 48V)",
    batt_mode_12v: "12V (1 аккумулятор 12V)",
    batt_mode_24v: "24V (2 аккумулятора 12V)",
    batt_mode_36v: "36V (3 аккумулятора 12V)",
    batt_mode_48v: "48V (4 аккумулятора 12V)",
    max_w_fmt: "{watts} Вт max",
    currency_rub: "руб",
    unit_kwh: "кВт⋅ч",
    rub_per_kwh: "руб/кВт⋅ч",

    // About Section
    about_app_desc: "Профессиональный мониторинг в реальном времени, защита и аналитика электросети для ИБП ExeGate SpecialPro",
    about_version_label: "Версия",
    about_release_label: "Релиз",
    about_license_label: "Лицензия",
    about_author_label: "Разработчик",
    about_btn_github: "Репозиторий на GitHub",
    about_btn_releases: "Релизы и обновления",
    about_btn_issues: "Сообщить об ошибке",
    about_feat_telemetry_title: "Телеметрия сети и AVR",
    about_feat_telemetry_desc: "Прямой опрос USB HID по протоколу Megatec F, точное отслеживание ступеней стабилизации AVR (Boost / Trim) и защита от лагов (Grace Period).",
    about_feat_models_title: "Поддержка любых моделей ИБП",
    about_feat_models_desc: "Готовые пресеты для SpecialPro UNB-1200, Smart LLB-2200, UNB-600/800/1500, LLB-3000 и Custom с автоопределением вольтажа АКБ (12V / 24V / 48V).",
    about_feat_shutdown_title: "Безопасное автовыключение Windows",
    about_feat_shutdown_desc: "Автоматическое корректное выключение ПК при разряде батареи с настраиваемым таймером, отменой в 1 клик, треем и Toast-уведомлениями.",
    about_feat_analytics_title: "Аналитика электросети и расходы",
    about_feat_analytics_desc: "Исторические графики, индекс стабильности сети, гистограмма пиковых часов просадок и расчет стоимости электроэнергии по тарифу.",
    about_hw_title: "Поддерживаемое оборудование и стек",
    about_hw_desc: "Линейка ExeGate SpecialPro UNB и Smart LLB (USB HID 0665:5161). Архитектура 65-байтных пакетов с защитой от зависаний чипа Cypress USB-Serial.",

    // Modal
    modal_log_title: "📜 Журнал событий питания",
    events_count_fmt: "{filtered} из {total} событий",

    // Status Modes
    mode_online: "СЕТЬ В НОРМЕ",
    mode_online_desc: "Питание от сети стабильное. Аккумулятор заряжен.",
    mode_battery: "ОТ БАТАРЕИ",
    mode_battery_desc: "Питание от встроенных аккумуляторов! Сеть отсутствует.",
    mode_avr_boost: "AVR СТАБИЛИЗАЦИЯ (ПОДЪЕМ)",
    mode_avr_boost_desc: "Просадка в сети ({in_v}V). Трансформатор повышает напряжение до {out_v}V.",
    mode_avr_trim: "AVR СТАБИЛИЗАЦИЯ (ПОНИЖЕНИЕ)",
    mode_avr_trim_desc: "Повышенное напряжение ({in_v}V). Трансформатор снижает до {out_v}V.",
    mode_avr: "AVR СТАБИЛИЗАЦИЯ",
    mode_avr_desc: "Стабилизация напряжения в сети ({in_v}V -> {out_v}V).",
    mode_disconnected: "ВОССТАНОВЛЕНИЕ СВЯЗИ...",
    mode_disconnected_desc: "Переподключение к USB ИБП..."
  }
};

let currentLang = 'en'; // Default language is English

function setLanguage(lang) {
  if (TRANSLATIONS[lang]) {
    currentLang = lang;
  }
}

function getLanguage() {
  return currentLang;
}

function t(key, replacements = {}) {
  const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
  let str = dict[key] || TRANSLATIONS.en[key] || key;
  for (const [param, value] of Object.entries(replacements)) {
    str = str.replace(new RegExp(`\\{${param}\\}`, 'g'), value);
  }
  return str;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { TRANSLATIONS, t, setLanguage, getLanguage };
}
