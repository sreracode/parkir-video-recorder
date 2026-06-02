from flask import Flask, request, jsonify
from camera_buffer import CameraBuffer
from datetime import datetime
import time, os, threading, uuid, yaml

app = Flask(__name__)

# ── Load config ──────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

RTSP_URL   = config["camera"]["rtsp_url"]
OUTPUT_DIR = config["paths"]["output_dir"]
PORT       = config["server"]["port"]
HOST       = config["server"]["host"]
# ─────────────────────────────────────────────────────────────

camera = CameraBuffer(RTSP_URL)

@app.route("/status")
def status():
    return jsonify({
        "connected"      : camera.is_connected(),
        "active_sessions": camera.active_sessions(),
        "total_recording": len(camera.active_sessions())
    })

@app.route("/start")
def start():
    notrans   = request.args.get("notrans", "unknown").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id  = f"{notrans}_{timestamp}_{uuid.uuid4().hex[:6]}"
    output_file = f"{OUTPUT_DIR}/{session_id}.avi"
    success = camera.start_recording(session_id, output_file)
    if success:
        return jsonify({"status": "ok", "session": session_id, "file": output_file})
    else:
        return jsonify({"status": "error", "message": "Gagal membuat VideoWriter"}), 500

@app.route("/stop")
def stop():
    session_id = request.args.get("notrans", "").replace(" ", "_")
    delay      = int(request.args.get("delay", 0))
    if not session_id:
        return jsonify({"status": "error", "message": "notrans (session_id) required"}), 400
    if delay > 0:
        def delayed_stop():
            time.sleep(delay)
            camera.stop_recording(session_id)
        threading.Thread(target=delayed_stop, daemon=True).start()
        return jsonify({"status": "ok", "message": f"Session '{session_id}' akan stop dalam {delay} detik"})
    else:
        saved = camera.stop_recording(session_id)
        if saved:
            return jsonify({"status": "ok", "file": saved})
        else:
            return jsonify({"status": "not_found", "session": session_id}), 404

@app.route("/stopall")
def stopall():
    sessions = camera.active_sessions()
    camera.stop_all()
    return jsonify({"status": "ok", "stopped": sessions})

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    camera.start()
    print(f"[Service] Recording service running at http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT)
