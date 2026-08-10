import asyncio
import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
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


app = FastAPI(title="ExeGate UPS SpecialPro UNB-1200 Dashboard", lifespan=lifespan)


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

