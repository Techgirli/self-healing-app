import time
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "healthy", "message": "Welcome to the Self-Healing Web App!"})

@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200

@app.route("/stress")
def stress():
    end_time = time.time() + 15
    while time.time() < end_time:
        _ = 999999 * 999999
    return jsonify({"status": "stressed", "message": "CPU spike completed."})

from flask import Flask, jsonify, Response

@app.route("/metrics")
def metrics():
    return Response("up 1\n", content_type="text/plain; version=0.0.4; charset=utf-8")   

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)   