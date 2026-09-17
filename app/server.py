import asyncio
import os
import json
import csv
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response, JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

from app.sound_manager import play_sound
from app.ups_driver import UPSDriver

ups_driver = UPSDriver()
active_websockets = set()
_ws_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ups_driver.start()
    asyncio.create_task(broadcast_loop())
    yield
    ups_driver.stop()


app = FastAPI(title="ExeGate SpecialPro UPS Dashboard", lifespan=lifespan)


@app.post("/api/play_sound")
async def api_play_sound(request: Request):
    try:
        data = await request.json()
        sound_type = data.get("type", "test")
    except Exception:
        sound_type = "test"
    play_sound(sound_type)
    return {"ok": True, "type": sound_type}

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path == "/" or path.startswith("/static/") or path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
        return response


app.add_middleware(NoCacheMiddleware)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def get_dashboard():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
        )
    return HTMLResponse("<h2>Dashboard index.html not found</h2>")


@app.get("/api/snapshot")
async def get_snapshot():
    return ups_driver.get_snapshot()


@app.get("/api/health")
async def health():
    snap = ups_driver.get_snapshot()
    st = snap.get("status") or {}
    return {
        "ok": True,
        "connected": bool(st.get("connected")),
        "timestamp": st.get("timestamp"),
        "mode": st.get("mode_code"),
    }


def compute_analytics(period: str = "7d"):
    now = datetime.now()
    if period == "24h":
        start_date = now - timedelta(hours=24)
        days_count = 1
    elif period == "7d":
        start_date = now - timedelta(days=7)
        days_count = 7
    elif period == "30d":
        start_date = now - timedelta(days=30)
        days_count = 30
    else:
        period = "all"
        start_date = datetime.min
        days_count = 31

    log_path = os.path.join(os.getcwd(), "ups_power_events.csv")
    rows = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for r in reader:
                    if len(r) >= 4 and r[0] and not r[0].startswith("Timestamp"):
                        try:
                            dt = datetime.strptime(r[0].strip(), "%Y-%m-%d %H:%M:%S")
                            if dt >= start_date:
                                rows.append({
                                    "dt": dt,
                                    "mode": (r[1] or "").upper(),
                                    "in_v": float(r[2]) if r[2] else 0.0,
                                    "out_v": float(r[3]) if r[3] else 0.0,
                                    "load_pct": float(r[4]) if len(r) > 4 and r[4] else 0.0
                                })
                        except Exception:
                            pass
        except Exception as e:
            pass

    rows.sort(key=lambda x: x["dt"])

    battery_events = 0
    avr_events = 0
    avr_boost = 0
    avr_trim = 0
    online_events = 0
    batt_duration_sec = 0.0
    valid_voltages = []

    hourly = [0] * 24
    daily_map = {}

    first_dt = rows[0]["dt"] if rows else now
    curr = (start_date if period != "all" else first_dt).date()
    end_curr = now.date()
    while curr <= end_curr:
        d_str = curr.strftime("%Y-%m-%d")
        daily_map[d_str] = {
            "date": d_str,
            "label": curr.strftime("%d.%m"),
            "battery": 0,
            "avr": 0,
            "total": 0
        }
        curr += timedelta(days=1)

    for i, r in enumerate(rows):
        m = r["mode"]
        h = r["dt"].hour
        d_str = r["dt"].strftime("%Y-%m-%d")
        if 0 <= h < 24:
            hourly[h] += 1

        if d_str not in daily_map:
            daily_map[d_str] = {
                "date": d_str,
                "label": r["dt"].strftime("%d.%m"),
                "battery": 0,
                "avr": 0,
                "total": 0
            }

        daily_map[d_str]["total"] += 1

        if "BATT" in m or "АКБ" in m or "БАТАР" in m:
            battery_events += 1
            daily_map[d_str]["battery"] += 1
            if i + 1 < len(rows):
                delta = (rows[i + 1]["dt"] - r["dt"]).total_seconds()
                if 0 < delta < 3600:
                    batt_duration_sec += delta
                else:
                    batt_duration_sec += 30.0
            else:
                batt_duration_sec += 30.0
        elif "AVR" in m or "СТАБИЛ" in m or "BOOST" in m or "TRIM" in m:
            avr_events += 1
            daily_map[d_str]["avr"] += 1
            if "TRIM" in m or "ПОНИЖ" in m:
                avr_trim += 1
            else:
                avr_boost += 1
        elif "ONLINE" in m or "НОРМ" in m:
            online_events += 1

        if r["in_v"] > 50.0:
            valid_voltages.append(r["in_v"])

    mins = int(batt_duration_sec // 60)
    secs = int(batt_duration_sec % 60)
    dur_str = f"{mins}m {secs}s" if mins < 60 else f"{mins // 60}h {mins % 60}m"
    dur_str_ru = f"{mins} мин {secs} сек" if mins < 60 else f"{mins // 60} ч {mins % 60} мин"

    period_total_hours = max(
        1.0, (now - (start_date if period != "all" else first_dt)).total_seconds() / 3600.0
    )
    outage_hours = batt_duration_sec / 3600.0
    stability = round(
        max(0.0, min(100.0, 100.0 * (1.0 - (outage_hours / period_total_hours)))), 2
    )

    settings = ups_driver.shutdown_manager.settings
    tariff = float(settings.get("electricity_tariff", 5.5))
    self_watts = float(settings.get("self_consumption_watts", 15.0))
    avg_load_watts = float(getattr(ups_driver, "energy_status", {}).get("load_watts", 120.0))
    total_watts_est = avg_load_watts + self_watts
    kwh_period_est = round((total_watts_est * period_total_hours) / 1000.0, 2)
    cost_period_est = round(kwh_period_est * tariff, 2)

    total_modes_count = battery_events + avr_events + max(1, online_events)
    battery_pct = round((battery_events / max(1, total_modes_count)) * 100, 1)
    avr_pct = round((avr_events / max(1, total_modes_count)) * 100, 1)
    online_pct = round(max(0.0, 100.0 - battery_pct - avr_pct), 1)

    return {
        "period": period,
        "summary": {
            "total_events": len(rows),
            "battery_events": battery_events,
            "avr_events": avr_events,
            "avr_boost_events": avr_boost,
            "avr_trim_events": avr_trim,
            "battery_duration_sec": int(batt_duration_sec),
            "battery_duration_str": dur_str,
            "battery_duration_str_ru": dur_str_ru,
            "stability_score": stability,
            "min_in_v": min(valid_voltages) if valid_voltages else 0.0,
            "avg_in_v": round(sum(valid_voltages) / len(valid_voltages), 1) if valid_voltages else 0.0,
            "max_in_v": max(valid_voltages) if valid_voltages else 0.0,
            "kwh_estimate": kwh_period_est,
            "cost_estimate": cost_period_est,
        },
        "daily_timeline": list(daily_map.values()),
        "modes_distribution": {
            "battery": battery_events,
            "avr": avr_events,
            "online": online_events,
            "battery_pct": battery_pct,
            "avr_pct": avr_pct,
            "online_pct": online_pct,
        },
        "hourly_distribution": hourly,
    }


@app.get("/api/analytics")
async def api_analytics(period: str = "7d"):
    data = compute_analytics(period=period)
    return JSONResponse(
        data,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@app.get("/api/download_csv")
async def download_csv():
    log_path = os.path.join(os.getcwd(), "ups_power_events.csv")
    if os.path.exists(log_path):
        return FileResponse(
            log_path,
            media_type="text/csv",
            filename="ups_power_events.csv",
            headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
        )
    return Response(content="CSV not found", status_code=404)


@app.get("/api/settings")
async def get_settings():
    return ups_driver.shutdown_manager.settings


@app.post("/api/settings")
async def update_settings(request: Request):
    try:
        new_data = await request.json()
        saved = ups_driver.shutdown_manager.save_settings(new_data)
        return {"ok": True, "settings": saved}
    except Exception as e:
        return Response(content=f"Error saving settings: {e}", status_code=400)


@app.post("/api/cancel_shutdown")
async def cancel_shutdown():
    lang = ups_driver.shutdown_manager.settings.get("language", "en")
    reason = "Canceled from web dashboard" if lang == "en" else "Отмена из веб-интерфейса"
    msg = "Auto shutdown canceled" if lang == "en" else "Автовыключение отменено"
    ok = ups_driver.shutdown_manager.cancel_shutdown(reason=reason)
    return {"ok": ok, "message": msg}


@app.post("/api/trigger_shutdown")
async def trigger_shutdown():
    lang = ups_driver.shutdown_manager.settings.get("language", "en")
    reason = "Test shutdown from settings" if lang == "en" else "Тестовая проверка из настроек"
    msg = "Test shutdown started (60 sec)" if lang == "en" else "Запущено тестовое выключение (60 сек)"
    ok = ups_driver.shutdown_manager.trigger_shutdown(reason=reason)
    return {"ok": ok, "message": msg}


@app.post("/api/reset_energy")
async def reset_energy():
    ups_driver.reset_accumulated_kwh()
    return {"ok": True}




@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async with _ws_lock:
        active_websockets.add(websocket)

    try:
        snapshot = ups_driver.get_snapshot()
        await websocket.send_text(json.dumps(snapshot))
    except Exception:
        pass

    try:
        while True:
            # Keepalive / ignore client pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        async with _ws_lock:
            active_websockets.discard(websocket)


async def broadcast_loop():
    last_seq = -1
    last_broadcast_time = 0.0

    while True:
        await asyncio.sleep(0.05)
        async with _ws_lock:
            clients = list(active_websockets)
        if not clients:
            continue

        snapshot = ups_driver.get_snapshot()
        st = snapshot.get("status") or {}
        cur_seq = st.get("seq", 0)
        now_t = asyncio.get_event_loop().time()

        if cur_seq != last_seq or (now_t - last_broadcast_time) > 3.0:
            last_seq = cur_seq
            last_broadcast_time = now_t
            payload = json.dumps(snapshot)
            disconnected = []
            for ws in clients:
                try:
                    await ws.send_text(payload)
                except Exception:
                    disconnected.append(ws)
            if disconnected:
                async with _ws_lock:
                    for ws in disconnected:
                        active_websockets.discard(ws)

