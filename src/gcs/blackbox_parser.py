"""
Blackbox Log Parser for ITU Sungur Autonomous Underwater Rocket
Parses telemetry records logged by the ESP32-S3 into 8MB PSRAM during autonomous missions.
"""

import struct
import csv
from typing import List, Dict, Any

RECORD_FORMAT = "<IffffBB"
# struct BlackboxLogRecord:
# uint32 timestamp_ms
# float depth_m
# float pitch_deg
# float heading_deg
# float motor_pwm
# uint8 fin_top_pwm_offset
# uint8 mission_state

class BlackboxParser:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def parse_binary(self, raw_bytes: bytes) -> List[Dict[str, Any]]:
        record_size = struct.calcsize(RECORD_FORMAT)
        count = len(raw_bytes) // record_size
        self.records.clear()

        for i in range(count):
            chunk = raw_bytes[i * record_size : (i + 1) * record_size]
            ts, depth, pitch, heading, motor, fin_offset, state = struct.unpack(RECORD_FORMAT, chunk)
            self.records.append({
                "timestamp_ms": ts,
                "depth_m": round(depth, 3),
                "pitch_deg": round(pitch, 2),
                "heading_deg": round(heading, 2),
                "motor_pwm": round(motor, 1),
                "fin_top_pwm": 1500 + fin_offset,
                "mission_state": state
            })
        return self.records

    def parse_csv_line(self, line: str) -> Dict[str, Any]:
        parts = [p.strip() for p in line.split(",")]
        return {
            "timestamp_ms": int(parts[0]),
            "depth_m": float(parts[1]),
            "pitch_deg": float(parts[2]),
            "heading_deg": float(parts[3]),
            "motor_pwm": float(parts[4]),
            "mission_state": int(parts[5]) if len(parts) > 5 else 0
        }

    def compute_summary(self) -> Dict[str, Any]:
        if not self.records:
            return {"error": "No records parsed"}

        depths = [r["depth_m"] for r in self.records]
        pitches = [r["pitch_deg"] for r in self.records]

        return {
            "total_records": len(self.records),
            "mission_duration_s": (self.records[-1]["timestamp_ms"] - self.records[0]["timestamp_ms"]) / 1000.0,
            "max_depth_m": max(depths),
            "avg_depth_m": round(sum(depths) / len(depths), 3),
            "max_pitch_deg": max(pitches),
            "min_pitch_deg": min(pitches)
        }

    def export_csv(self, filename: str):
        if not self.records:
            return
        keys = self.records[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.records)
