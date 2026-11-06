import os
import sys
import json
import time
from flask import Flask, jsonify, send_from_directory, request, Response
from flask_sock import Sock
from ups_box_driver import BoxUPSDriver

app = Flask(__name__, static_folder="static")
sock = Sock(app)

driver = BoxUPSDriver()
driver.start()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

@app.route("/api/snapshot")
def api_snapshot():
    return jsonify(driver.get_snapshot())

@app.route("/api/history")
def api_history():
    return jsonify({"history": list(driver.history)})

@app.route("/api/events")
def api_events():
    return jsonify({"events": list(driver.events)})

@app.route("/api/download_csv")
def api_download_csv():
    if os.path.exists(driver.log_file):
        return send_from_directory(driver.data_dir, "ups_power_events.csv", as_attachment=True)
    return Response("Timestamp,Mode,Input_V,Output_V,Load_Pct,Battery_V,Temp_C,Status_Bits\n", mimetype="text/csv")

@app.route("/api/play_sound", methods=["POST"])
def api_play_sound():
    return jsonify({"ok": True})

@app.route("/api/test_telegram", methods=["POST", "GET"])
def api_test_telegram():
    snap = driver.get_snapshot()
    st = snap.get("status", {})
    msg = (
        f"⚡ <b>Тестовое оповещение мониторинга сети:</b>\n\n"
        f"🔌 Статус сети: <b>{st.get('mode_title_ru', 'Сеть')}</b>\n"
        f"📉 Входное напряжение: <b>{st.get('in_v', 0.0)} В</b>\n"
        f"⚡ Выход ИБП: <b>{st.get('out_v', 0.0)} В</b>\n"
        f"🔋 Заряд АКБ: <b>{st.get('batt_pct', 0)}%</b> ({st.get('batt_v', 0.0)} В)\n"
        f"💡 Нагрузка: <b>{st.get('load_pct', 0)}%</b> (~{st.get('load_watts', 0)} Вт)\n"
        f"🕒 Время: {st.get('time_short', '--:--:--')}\n"
        f"✅ Мониторинг круглосуточно работает на ТВ-приставке!"
    )
    driver.send_telegram(msg)
    return jsonify({"ok": True, "sent": True, "message": msg})

@sock.route("/ws")
def ws_telemetry(ws):
    last_seq = -1
    while True:
        try:
            snap = driver.get_snapshot()
            cur_seq = snap["status"].get("seq", 0)
            if cur_seq != last_seq:
                last_seq = cur_seq
                ws.send(json.dumps(snap))
            time.sleep(1.0)
        except Exception:
            break

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8089, debug=False)