from flask import Flask, request, jsonify
from camera_buffer import CameraBuffer
import time, os, threading, yaml, cv2

app = Flask(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

RTSP_URL   = config["camera"]["rtsp_url"]
FOTO_DIR   = config["paths"].get("foto_dir", config["paths"]["output_dir"])
VIDEO_DIR  = config["paths"]["output_dir"]
PORT       = config["server"]["port"]
HOST       = config["server"]["host"]

camera = CameraBuffer(RTSP_URL)


def parse_notrans_path(notrans, base_dir):
    """
    Parse notrans format: 01{gate}{YYMMDD}{counter}
    Example: 012602180026 -> gate=01, YY=26, MM=02, DD=18, counter=0026
    Returns folder path: base_dir/20YYMM/DD
    """
    if len(notrans) < 12:
        return base_dir
    yy = notrans[2:4]
    mm = notrans[4:6]
    dd = notrans[6:8]
    if not (yy.isdigit() and mm.isdigit() and dd.isdigit()):
        return base_dir
    subfolder = f"20{yy}{mm}/{dd}"
    return os.path.join(base_dir, subfolder)


@app.route("/status")
def status():
    return jsonify({
        "connected"      : camera.is_connected(),
        "active_sessions": camera.active_sessions(),
        "total_recording": len(camera.active_sessions()),
        "foto_dir"       : FOTO_DIR,
        "video_dir"      : VIDEO_DIR,
    })


@app.route("/snapshot")
def snapshot():
    """Capture single frame and save as JPEG. Overwrites if exists."""
    notrans = request.args.get("notrans", "unknown").replace(" ", "_")
    output_dir = parse_notrans_path(notrans, FOTO_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{notrans}.jpg")

    frame = camera.get_current_frame()
    if frame is None:
        return jsonify({"status": "error", "message": "No frame available"}), 503

    cv2.imwrite(output_file, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return jsonify({
        "status": "ok",
        "file": output_file,
        "notrans": notrans
    })


@app.route("/start")
def start():
    notrans = request.args.get("notrans", "unknown").replace(" ", "_")

    output_dir = parse_notrans_path(notrans, VIDEO_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{notrans}.avi")

    # Stop existing recording for same notrans if any
    camera.stop_recording(notrans)

    success = camera.start_recording(notrans, output_file)
    if success:
        return jsonify({"status": "ok", "session": notrans, "file": output_file})
    else:
        return jsonify({"status": "error", "message": "Gagal membuat VideoWriter"}), 500


@app.route("/stop")
def stop():
    session_id = request.args.get("notrans", "").replace(" ", "_")
    delay = int(request.args.get("delay", 0))
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
    os.makedirs(FOTO_DIR, exist_ok=True)
    os.makedirs(VIDEO_DIR, exist_ok=True)
    camera.start()
    print(f"[Service] Camera service running at http://{HOST}:{PORT}")
    print(f"  Foto dir : {FOTO_DIR}")
    print(f"  Video dir: {VIDEO_DIR}")
    app.run(host=HOST, port=PORT)
