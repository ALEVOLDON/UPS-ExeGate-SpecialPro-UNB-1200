"""Megatec F protocol parser and battery percentage estimation for ExeGate UNB-1200."""

def estimate_battery_pct(batt_v: float, on_battery: bool, is_batt_low: bool) -> int:
    """Estimate battery percentage based on battery voltage and state."""
    try:
        v = float(batt_v)
    except (TypeError, ValueError):
        return 0

    if is_batt_low:
        return max(0, min(10, int(round((v - 10.0) * 8))))

    if not on_battery:
        if v >= 12.70: return 100
        if v >= 12.55: return 97
        if v >= 12.40: return 92
        if v >= 12.25: return 85
        if v >= 12.10: return 75
        if v >= 11.95: return 65
        if v >= 11.80: return 50
        if v >= 11.55: return 35
        if v >= 11.25: return 20
        return 10

    points = [
        (12.60, 100), (12.45, 90), (12.30, 80), (12.15, 70),
        (12.00, 55), (11.80, 40), (11.55, 25), (11.25, 12), (10.20, 0)
    ]
    if v >= points[0][0]: return 100
    if v <= points[-1][0]: return 0
    for i in range(len(points) - 1):
        v_hi, p_hi = points[i]
        v_lo, p_lo = points[i + 1]
        if v_lo <= v <= v_hi:
            span = v_hi - v_lo
            t = (v - v_lo) / span if span else 0.0
            return int(round(p_lo + t * (p_hi - p_lo)))
    return 0


def parse_f_response(raw_text: str):
    """
    Parse Megatec F protocol telemetry string.
    Format: F(MMM.M NNN.N PPP.P QQQ RR.R S.SS TT.T b7b6b5b4b3b2b1b0
    Example: F(204.0 000.0 247.0 016 49.0 12.8 30.8 00001001
    """
    text = raw_text.strip()
    if 'F(' in text:
        text = text[text.find('F(') + 2:]
    elif '(' in text:
        text = text[text.find('(') + 1:]
    else:
        return None

    clean_text = "".join(ch for ch in text if ch.isdigit() or ch in '. ')
    parts = clean_text.split()
    if len(parts) < 8:
        return None

    try:
        in_v = float(parts[0])
        fault_v = float(parts[1])
        out_v = float(parts[2])
        load_pct = int(parts[3])
        freq = float(parts[4])
        batt_v = float(parts[5])
        temp = float(parts[6])
        status_bits = parts[7]

        is_battery = status_bits[0] == '1' if len(status_bits) >= 1 else False
        is_batt_low = status_bits[1] == '1' if len(status_bits) >= 2 else False
        avr_bit = status_bits[2] == '1' if len(status_bits) >= 3 else False

        # AVR is active if flagged by hardware bit or if output voltage deviates significantly from input while on mains
        v_diff = out_v - in_v
        is_avr_boost = (not is_battery) and (avr_bit or v_diff >= 12 or (in_v > 0 and in_v <= 210 and out_v > in_v + 6))
        is_avr_trim = (not is_battery) and ((avr_bit and v_diff <= -12) or (in_v >= 245 and v_diff <= -8))
        is_avr = is_avr_boost or is_avr_trim

        batt_pct = estimate_battery_pct(batt_v, is_battery, is_batt_low)
        load_watts = int(750 * (load_pct / 100.0))

        if is_battery:
            mode_code = "BATTERY"
            mode_title = "ON BATTERY"
            mode_title_ru = "ОТ БАТАРЕИ"
            mode_desc = "Running on internal batteries! Mains power lost."
            mode_desc_ru = "Питание от встроенных аккумуляторов! Сеть отсутствует."
            status_color = "#f59e0b"
        elif is_avr_boost:
            mode_code = "AVR_BOOST"
            mode_title = "AVR BOOST"
            mode_title_ru = "AVR СТАБИЛИЗАЦИЯ (ПОДЪЕМ)"
            mode_desc = f"Grid voltage drop ({in_v}V). Boosting output to {out_v}V."
            mode_desc_ru = f"Просадка в сети ({in_v}V). Трансформатор повышает напряжение до {out_v}V."
            status_color = "#3b82f6"
        elif is_avr_trim:
            mode_code = "AVR_TRIM"
            mode_title = "AVR TRIM"
            mode_title_ru = "AVR СТАБИЛИЗАЦИЯ (ПОНИЖЕНИЕ)"
            mode_desc = f"High grid voltage ({in_v}V). Trimming output to {out_v}V."
            mode_desc_ru = f"Повышенное напряжение ({in_v}V). Трансформатор снижает до {out_v}V."
            status_color = "#6366f1"
        elif is_avr:
            mode_code = "AVR"
            mode_title = "AVR STABILIZATION"
            mode_title_ru = "AVR СТАБИЛИЗАЦИЯ"
            mode_desc = f"Mains voltage stabilization ({in_v}V -> {out_v}V)."
            mode_desc_ru = f"Стабилизация напряжения в сети ({in_v}V -> {out_v}V)."
            status_color = "#3b82f6"
        else:
            mode_code = "ONLINE"
            mode_title = "ONLINE"
            mode_title_ru = "СЕТЬ В НОРМЕ"
            mode_desc = "Mains power stable. Battery fully charged."
            mode_desc_ru = "Питание от сети стабильное. Аккумулятор заряжен."
            status_color = "#10b981"

        return {
            "in_v": in_v,
            "fault_v": fault_v,
            "out_v": out_v,
            "load_pct": load_pct,
            "load_watts": load_watts,
            "freq": freq,
            "batt_v": batt_v,
            "batt_pct": batt_pct,
            "temp": temp,
            "status_bits": status_bits,
            "raw_frame": f"F({' '.join(parts[:8])})",
            "is_battery": is_battery,
            "is_batt_low": is_batt_low,
            "is_avr": is_avr,
            "is_avr_boost": is_avr_boost,
            "is_avr_trim": is_avr_trim,
            "mode_code": mode_code,
            "mode_title": mode_title,
            "mode_title_ru": mode_title_ru,
            "mode_desc": mode_desc,
            "mode_desc_ru": mode_desc_ru,
            "status_color": status_color
        }
    except Exception:
        return None
