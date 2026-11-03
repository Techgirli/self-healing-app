import time
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "healthy", "message": "Welcome to the Self-Healing Web App!"})

@app.route("/health")
def health():
    # Standard health check endpoint for Docker / orchestration
    return jsonify({"status": "UP"}), 200

@app.route("/stress")
def stress():
    # Intentionally spike CPU to simulate a runaway process or heavy load
    end_time = time.time() + 15  # 15 seconds of intense computation
    while time.time() < end_time:
        _ = 999999 * 999999
    return jsonify({"status": "stressed", "message": "CPU spike completed."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
