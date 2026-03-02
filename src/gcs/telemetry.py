import json
import time

class TelemetrySerializer:
    def __init__(self, vehicle_id="ROCKET-01"):
        self.vehicle_id = vehicle_id

    def serialize(self, state, sensor_data):
        payload = {
            "v_id": self.vehicle_id,
            "ts": time.time(),
            "state": state,
            "data": {
                "alt": round(sensor_data.get('altitude', 0), 2),
                "vel_z": round(sensor_data.get('velocity_z', 0), 2),
                "acc_z": round(sensor_data.get('accel_z', 0), 2),
                "batt": round(sensor_data.get('battery', 0), 1)
            }
        }
        return json.dumps(payload)

if __name__ == "__main__":
    ts = TelemetrySerializer()
    mock_data = {'altitude': 120.5, 'velocity_z': -5.2, 'accel_z': 9.81, 'battery': 12.6}
    print(ts.serialize("DESCENDING", mock_data))
