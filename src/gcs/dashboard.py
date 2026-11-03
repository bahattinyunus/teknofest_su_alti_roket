"""
Interactive Ground Control Station (GCS) Dashboard & Real-Time Telemetry Monitor
Serves a responsive aerospace-style web interface at http://localhost:8080 with zero external dependencies.
Features Artificial Horizon (ADI), Heading Compass, Depth Gauge, Fin Deflections, and Safe-to-Arm status.
"""

import http.server
import socketserver
import threading
import json
import time
import math
import webbrowser
import os
import sys
from typing import Dict, Any

PORT = 8080

# Shared state between telemetry feed and HTTP server
s_currentTelemetry: Dict[str, Any] = {
    "timestamp": time.time(),
    "depth_m": 1.50,
    "pitch_deg": 0.0,
    "roll_deg": 0.0,
    "heading_deg": 90.0,
    "surge_m_s": 2.20,
    "motor_pwm": 1750,
    "fin1_deg": 0.0,
    "fin2_deg": 0.0,
    "fin3_deg": 0.0,
    "fin4_deg": 0.0,
    "mission_state": "CRUISE_50M",
    "safe_to_arm": False,
    "battery_v": 15.2,
    "cpu_load_pct": 18
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SUNGUR GCS — Autonomous Underwater Rocket Telemetry</title>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #131b2e;
      --border: #1e293b;
      --accent: #00d2ff;
      --accent2: #3a7bd5;
      --success: #10b981;
      --danger: #ef4444;
      --warning: #f59e0b;
      --text: #f1f5f9;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 16px;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 16px;
    }
    h1 { font-size: 1.25rem; font-weight: 700; color: var(--accent); letter-spacing: 0.5px; }
    .badge {
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      background: #1e293b;
    }
    .badge.active { background: rgba(16, 185, 129, 0.2); color: var(--success); border: 1px solid var(--success); }
    .badge.danger { background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid var(--danger); }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      position: relative;
    }
    .card h2 {
      font-size: 0.85rem;
      text-transform: uppercase;
      color: var(--muted);
      letter-spacing: 1px;
      margin-bottom: 12px;
    }
    .canvas-container {
      display: flex;
      justify-content: center;
      align-items: center;
      margin: auto;
    }
    canvas { background: transparent; }
    .metric-row {
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 0.9rem;
    }
    .metric-row:last-child { border: none; }
    .metric-val { font-weight: 600; font-family: monospace; color: var(--accent); }
    .fin-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .fin-box {
      background: #0f172a;
      padding: 10px;
      border-radius: 8px;
      text-align: center;
      border: 1px solid var(--border);
    }
    .fin-label { font-size: 0.75rem; color: var(--muted); }
    .fin-val { font-size: 1.1rem; font-weight: bold; color: var(--accent); margin-top: 4px; }
    .safe-badge {
      display: inline-block;
      text-align: center;
      padding: 12px;
      border-radius: 8px;
      font-weight: bold;
      letter-spacing: 1px;
      margin-top: 8px;
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>🚀 TEKNOFEST SU ALTI ROKETİ GCS</h1>
      <p style="font-size: 0.8rem; color: var(--muted);">Real-Time Avionics & Navigation Flight Monitor</p>
    </div>
    <div style="display: flex; gap: 8px; align-items: center;">
      <span id="stateBadge" class="badge active">STANDBY</span>
      <span id="connBadge" class="badge active">LIVE 50Hz</span>
    </div>
  </header>

  <div class="grid">
    <!-- Artificial Horizon (ADI) -->
    <div class="card">
      <h2>Attitude Director (ADI)</h2>
      <div class="canvas-container">
        <canvas id="adiCanvas" width="220" height="220"></canvas>
      </div>
      <div class="metric-row" style="margin-top: 12px;">
        <span>Pitch Angle:</span>
        <span id="pitchVal" class="metric-val">0.0°</span>
      </div>
      <div class="metric-row">
        <span>Roll Angle:</span>
        <span id="rollVal" class="metric-val">0.0°</span>
      </div>
    </div>

    <!-- Depth & Heading -->
    <div class="card">
      <h2>Depth & Heading Compass</h2>
      <div class="canvas-container">
        <canvas id="compassCanvas" width="220" height="150"></canvas>
      </div>
      <div class="metric-row" style="margin-top: 8px;">
        <span>Hydrostatic Depth:</span>
        <span id="depthVal" class="metric-val" style="font-size: 1.2rem; color: #10b981;">0.00 m</span>
      </div>
      <div class="metric-row">
        <span>Forward Velocity (Surge):</span>
        <span id="speedVal" class="metric-val">0.0 m/s</span>
      </div>
      <div class="metric-row">
        <span>Compass Heading:</span>
        <span id="headingVal" class="metric-val">000°</span>
      </div>
    </div>

    <!-- Actuator Fins & Motor -->
    <div class="card">
      <h2>X-Rudder Actuators</h2>
      <div class="fin-grid">
        <div class="fin-box">
          <div class="fin-label">FIN 1 (Top-Left)</div>
          <div id="fin1Val" class="fin-val">0.0°</div>
        </div>
        <div class="fin-box">
          <div class="fin-label">FIN 2 (Top-Right)</div>
          <div id="fin2Val" class="fin-val">0.0°</div>
        </div>
        <div class="fin-box">
          <div class="fin-label">FIN 3 (Bottom-Left)</div>
          <div id="fin3Val" class="fin-val">0.0°</div>
        </div>
        <div class="fin-box">
          <div class="fin-label">FIN 4 (Bottom-Right)</div>
          <div id="fin4Val" class="fin-val">0.0°</div>
        </div>
      </div>
      <div class="metric-row" style="margin-top: 12px;">
        <span>Main BLDC Motor:</span>
        <span id="motorVal" class="metric-val">1500 µs (STOP)</span>
      </div>
    </div>

    <!-- Mission & Safe-to-Arm Interlock -->
    <div class="card">
      <h2>Payload & Safety Interlock</h2>
      <div class="metric-row">
        <span>Active Mission State:</span>
        <span id="missionVal" class="metric-val">IDLE</span>
      </div>
      <div class="metric-row">
        <span>Battery (4S Li-Po):</span>
        <span id="battVal" class="metric-val">15.2 V</span>
      </div>
      <div class="metric-row">
        <span>FreeRTOS Core Load:</span>
        <span id="cpuVal" class="metric-val">18 %</span>
      </div>
      <div id="armStatus" class="safe-badge" style="background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid var(--danger);">
        🔒 SAFE-TO-ARM: LOCKED (SUBMERGED)
      </div>
    </div>
  </div>

  <script>
    function drawADI(pitch, roll) {
      const c = document.getElementById("adiCanvas");
      const ctx = c.getContext("2d");
      const cx = c.width / 2;
      const cy = c.height / 2;
      const r = 90;

      ctx.clearRect(0, 0, c.width, c.height);

      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();

      // Rotate with roll
      ctx.translate(cx, cy);
      ctx.rotate(roll * Math.PI / 180);

      // Translate with pitch (3 pixels per degree)
      const pitchOffset = Math.max(-r, Math.min(r, pitch * 2.5));

      // Sky
      ctx.fillStyle = "#1e3a8a";
      ctx.fillRect(-r*2, -r*2 + pitchOffset, r*4, r*2);

      // Sea / Ground
      ctx.fillStyle = "#854d0e";
      ctx.fillRect(-r*2, pitchOffset, r*4, r*2);

      // Horizon line
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(-r, pitchOffset);
      ctx.lineTo(r, pitchOffset);
      ctx.stroke();

      ctx.restore();

      // Reticle
      ctx.strokeStyle = "#00d2ff";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(cx - 30, cy); ctx.lineTo(cx - 10, cy);
      ctx.moveTo(cx + 10, cy); ctx.lineTo(cx + 30, cy);
      ctx.moveTo(cx, cy - 10); ctx.lineTo(cx, cy + 10);
      ctx.stroke();

      // Outer bezel
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();
    }

    function drawCompass(heading) {
      const c = document.getElementById("compassCanvas");
      const ctx = c.getContext("2d");
      ctx.clearRect(0, 0, c.width, c.height);

      const cx = c.width / 2;
      const cy = 70;
      const r = 50;

      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(-heading * Math.PI / 180);

      // North needle
      ctx.fillStyle = "#ef4444";
      ctx.beginPath();
      ctx.moveTo(0, -r + 8);
      ctx.lineTo(-8, 0);
      ctx.lineTo(8, 0);
      ctx.fill();

      // South needle
      ctx.fillStyle = "#94a3b8";
      ctx.beginPath();
      ctx.moveTo(0, r - 8);
      ctx.lineTo(-8, 0);
      ctx.lineTo(8, 0);
      ctx.fill();

      ctx.restore();
    }

    async function pollTelemetry() {
      try {
        const res = await fetch("/api/telemetry");
        const data = await res.json();

        document.getElementById("pitchVal").innerText = data.pitch_deg.toFixed(1) + "°";
        document.getElementById("rollVal").innerText = data.roll_deg.toFixed(1) + "°";
        document.getElementById("depthVal").innerText = data.depth_m.toFixed(2) + " m";
        document.getElementById("speedVal").innerText = data.surge_m_s.toFixed(2) + " m/s";
        document.getElementById("headingVal").innerText = Math.round(data.heading_deg).toString().padStart(3, "0") + "°";
        document.getElementById("stateBadge").innerText = data.mission_state;
        document.getElementById("missionVal").innerText = data.mission_state;
        document.getElementById("motorVal").innerText = data.motor_pwm + " µs";
        document.getElementById("battVal").innerText = data.battery_v.toFixed(1) + " V";
        document.getElementById("cpuVal").innerText = data.cpu_load_pct + " %";

        document.getElementById("fin1Val").innerText = data.fin1_deg.toFixed(1) + "°";
        document.getElementById("fin2Val").innerText = data.fin2_deg.toFixed(1) + "°";
        document.getElementById("fin3Val").innerText = data.fin3_deg.toFixed(1) + "°";
        document.getElementById("fin4Val").innerText = data.fin4_deg.toFixed(1) + "°";

        const armEl = document.getElementById("armStatus");
        if (data.safe_to_arm) {
          armEl.style.background = "rgba(16, 185, 129, 0.2)";
          armEl.style.color = "var(--success)";
          armEl.style.borderColor = "var(--success)";
          armEl.innerText = "🚀 SAFE-TO-ARM: ARMED (READY TO FIRE)";
        } else {
          armEl.style.background = "rgba(239, 68, 68, 0.2)";
          armEl.style.color = "var(--danger)";
          armEl.style.borderColor = "var(--danger)";
          armEl.innerText = "🔒 SAFE-TO-ARM: LOCKED (SUBMERGED)";
        }

        drawADI(data.pitch_deg, data.roll_deg);
        drawCompass(data.heading_deg);
      } catch (err) {
        // console.error(err);
      }
    }

    setInterval(pollTelemetry, 100);
  </script>
</body>
</html>
"""

class GCSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif self.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(s_currentTelemetry).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        # Silence standard HTTP access logging in console
        pass

def run_telemetry_simulation():
    """Generates a realistic autonomous mission flight profile for demonstration and testing."""
    t0 = time.time()
    while True:
        elapsed = time.time() - t0
        # Phase 1: 0 - 10s (Dive to 1.5m)
        if elapsed < 10.0:
            s_currentTelemetry["mission_state"] = "DIVING_1.5M"
            s_currentTelemetry["depth_m"] = min(1.50, elapsed * 0.15)
            s_currentTelemetry["pitch_deg"] = -12.0
            s_currentTelemetry["motor_pwm"] = 1750
            s_currentTelemetry["surge_m_s"] = 2.1
            s_currentTelemetry["safe_to_arm"] = False
        # Phase 2: 10 - 25s (Cruise 50m)
        elif elapsed < 25.0:
            s_currentTelemetry["mission_state"] = "CRUISE_50M"
            s_currentTelemetry["depth_m"] = 1.50 + 0.05 * math.sin(elapsed)
            s_currentTelemetry["pitch_deg"] = 0.5 * math.sin(elapsed)
            s_currentTelemetry["motor_pwm"] = 1800
            s_currentTelemetry["safe_to_arm"] = False
        # Phase 3: 25 - 32s (180 Turn)
        elif elapsed < 32.0:
            s_currentTelemetry["mission_state"] = "TURN_180"
            turn_progress = (elapsed - 25.0) / 7.0
            s_currentTelemetry["heading_deg"] = (90.0 + turn_progress * 180.0) % 360.0
            s_currentTelemetry["fin1_deg"] = -15.0
            s_currentTelemetry["fin2_deg"] = 15.0
        # Phase 4: 32 - 45s (Yunuslama / Pitch Up & Surface Launch)
        elif elapsed < 45.0:
            s_currentTelemetry["mission_state"] = "YUNUSLAMA_SURFACE"
            surf_progress = (elapsed - 32.0) / 10.0
            s_currentTelemetry["depth_m"] = max(0.0, 1.50 * (1.0 - surf_progress))
            s_currentTelemetry["pitch_deg"] = 38.0
            if s_currentTelemetry["depth_m"] <= 0.04 and s_currentTelemetry["pitch_deg"] >= 30.0:
                s_currentTelemetry["safe_to_arm"] = True
                s_currentTelemetry["mission_state"] = "ROCKET_ARMED_FIRE"
        else:
            t0 = time.time() # Loop demo

        time.sleep(0.05)

def start_server(open_browser: bool = False):
    # Enable SO_REUSEADDR
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("", PORT), GCSRequestHandler)

    t_sim = threading.Thread(target=run_telemetry_simulation, daemon=True)
    t_sim.start()

    print(f"=== SUNGUR UNDERWATER ROCKET GCS SERVER STARTED ===")
    print(f"Listening on: http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")

    if open_browser:
        webbrowser.open(f"http://localhost:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping GCS server...")
        server.shutdown()

if __name__ == "__main__":
    auto_open = "--no-browser" not in sys.argv
    start_server(open_browser=auto_open)
