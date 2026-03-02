import time

class MissionFSM:
    # 2026 Specification States
    STATES = [
        "IDLE", 
        "STAGE_1_START", "STAGE_1_10M", "STAGE_1_50M", "STAGE_1_RETURN", 
        "STAGE_2_START", "STAGE_2_30M", "STAGE_2_SURFACE", "STAGE_2_LAUNCH",
        "RECOVERY", "EMERGENCY_STOP"
    ]

    def __init__(self):
        self.state = "IDLE"
        self.start_time = None
        self.distance_traveled = 0
        self.mission_mode = 1 # 1 for Stage-1, 2 for Stage-2

    def update(self, sensor_data):
        """
        sensor_data: {
            'accel_z': float, 
            'velocity_z': float, 
            'dist_x': float, # Distance from shore
            'pitch': float, 
            'is_armed': bool
        }
        """
        if self.state == "IDLE":
            if sensor_data.get('is_armed'):
                self.state = "STAGE_1_START" if self.mission_mode == 1 else "STAGE_2_START"
                self.start_time = time.time()

        # STAGE 1: NAVIGATION & RETURN
        elif self.state == "STAGE_1_START":
            if sensor_data['dist_x'] >= 10:
                self.transition_to("STAGE_1_10M")
        
        elif self.state == "STAGE_1_10M":
            if sensor_data['dist_x'] >= 50:
                self.transition_to("STAGE_1_50M")
        
        elif self.state == "STAGE_1_50M":
            # Logic to turn back
            self.transition_to("STAGE_1_RETURN")
            
        elif self.state == "STAGE_1_RETURN":
            if sensor_data['dist_x'] <= 10:
                self.transition_to("RECOVERY")

        # STAGE 2: ROKET ATEŞLEME
        elif self.state == "STAGE_2_START":
            if sensor_data['dist_x'] >= 30:
                self.transition_to("STAGE_2_30M")

        elif self.state == "STAGE_2_30M":
            # Start pitch up to surface
            if sensor_data['pitch'] > 45: # Example pitch angle for surfacing
                self.transition_to("STAGE_2_SURFACE")

        elif self.state == "STAGE_2_SURFACE":
            # Check stabilization before launch
            self.transition_to("STAGE_2_LAUNCH")

        elif self.state == "STAGE_2_LAUNCH":
            # Trigger ignition
            time.sleep(1) # Simulated delay
            self.transition_to("RECOVERY")

    def transition_to(self, new_state):
        if new_state in self.STATES:
            print(f"[MISSION] {self.state} -> {new_state}")
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
