"""
Flask Web Dashboard + REST API for Smart Campus NMS
- Serves frontend/index.html as UI
- Exposes /api/devices to return latest status as JSON
"""

import os
import csv
from flask import Flask, jsonify, send_from_directory

LOG_FILE = os.path.join("data", "nms_log_v2.csv")

app = Flask(__name__)


def read_latest_status():
    """
    Reads CSV and returns latest record per device.
    Structure: { device_name: { ...row } }
    """
    if not os.path.exists(LOG_FILE):
        return {}

    latest = {}
    with open(LOG_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            device = row["device"]
            latest[device] = row  # last entry becomes latest
    return latest


# ---------- REST API ----------
@app.get("/api/devices")
def api_devices():
    latest = read_latest_status()
    return jsonify(list(latest.values()))


# ---------- FRONTEND ----------
@app.get("/")
def index():
    # Serve frontend/index.html from project root
    return send_from_directory("../frontend", "index.html")


if __name__ == "__main__":
    # run from project root: python code/web_app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
