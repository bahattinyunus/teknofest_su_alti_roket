import time

class RocketFSM:
    STATES = ["IDLE", "ARMED", "LAUNCH", "DESCENDING", "RECOVERY"]

    def __init__(self):
        self.state = "IDLE"
        self.launch_time = None
        self.is_armed = False

    def update(self, sensor_data):
        if self.state == "IDLE":
            if self.is_armed:
                self.transition_to("ARMED")
        
        elif self.state == "ARMED":
            if sensor_data['accel_z'] > 20: # Threshold for launch detection
                self.transition_to("LAUNCH")
                self.launch_time = time.time()
        
        elif self.state == "LAUNCH":
            if sensor_data['velocity_z'] < 0:
                self.transition_to("DESCENDING")
        
        elif self.state == "DESCENDING":
            if sensor_data['altitude'] < 5: # Close to ground/water level
                self.transition_to("RECOVERY")

    def transition_to(self, new_state):
        if new_state in self.STATES:
            print(f"[FSM] Transitioning from {self.state} to {new_state}")
            self.state = new_state

def main():
    fsm = RocketFSM()
    print("Rocket Flight Software Initialized.")
    
    # Mock loop
    try:
        while True:
            # Placeholder for sensor reading logic
            sensor_data = {
                'accel_z': 0,
                'velocity_z': 0,
                'altitude': 100
            }
            fsm.update(sensor_data)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Software Terminated.")

if __name__ == "__main__":
    main()
