const TRANSLATIONS = {
  en: {
    app_title: "ExeGate SpecialPro UNB-1200 — UPS Monitor",
    brand_name: "ExeGate Pro",
    brand_sub: "UNB-1200 · USB HID",

    // Navigation
    nav_overview: "Overview",
    nav_flow: "Power Flow",
    nav_analytics: "Analytics",
    nav_events: "Event Log",
    nav_settings: "Settings",

    sidebar_connected: "CONNECTED",
    sidebar_disconnected: "DISCONNECTED",

    // Header Views
    view_dashboard: "Monitoring Dashboard",
    view_flow: "Interactive Power Flow Scheme",
    view_analytics: "Analytics & Voltage Dynamics",
    view_events: "Power Event Log",
    view_settings: "Alerts & System Settings",

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
    analytics_title: "Detailed Voltage Dynamics Graph",
    analytics_sub: "Mains Input Voltage vs UPS Output Voltage",

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
    currency_rub: "₽",
    unit_kwh: "kWh",
    rub_per_kwh: "₽/kWh",

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
    app_title: "ExeGate SpecialPro UNB-1200 — Мониторинг ИБП",
    brand_name: "ExeGate Pro",
    brand_sub: "UNB-1200 · USB HID",

    // Navigation
    nav_overview: "Обзор",
    nav_flow: "Схема питания",
    nav_analytics: "Аналитика",
    nav_events: "Журнал",
    nav_settings: "Настройки",

    sidebar_connected: "ПОДКЛЮЧЕНО",
    sidebar_disconnected: "НЕТ СВЯЗИ",

    // Header Views
    view_dashboard: "Дашборд мониторинга",
    view_flow: "Интерактивная схема питания",
    view_analytics: "Аналитика и динамика напряжений",
    view_events: "Журнал событий питания",
    view_settings: "Настройки оповещений и системы",

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
    analytics_title: "Детальный график динамики напряжений",
    analytics_sub: "Входное напряжение vs Выходное напряжение ИБП",

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
    currency_rub: "руб",
    unit_kwh: "кВт⋅ч",
    rub_per_kwh: "руб/кВт⋅ч",

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
