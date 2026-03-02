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
    fsm = MissionFSM()
    print("--- TEKNOFEST 2026 SARA Mission Software ---")
    
    # Simulation variables
    dt = 0.1 # 100ms
    dist_x = 0
    velocity_x = 0
    pitch = 0
    is_armed = True
    
    # Set Mission Mode (1: Stage-1, 2: Stage-2)
    fsm.mission_mode = 2 
    print(f"Active Mission: STAGE_{fsm.mission_mode}")

    try:
        while fsm.state != "RECOVERY":
            # Simple Physics Simulation
            # Always progress forward if not in RECOVERY or EMERGENCY_STOP
            if "STAGE" in fsm.state:
                velocity_x = 1.5 # m/s (Constant forward thrust)
                dist_x += velocity_x * dt
            
            # Mission specific logic
            if "STAGE_2_30M" in fsm.state:
                pitch += 10 # Rapid pitch up for surfacing
            
            sensor_data = {
                'accel_z': 0,
                'velocity_z': 0,
                'dist_x': dist_x,
                'pitch': pitch,
                'is_armed': is_armed
            }
            
            fsm.update(sensor_data)
            
            if fsm.state != "RECOVERY":
                print(f"[SIM] Dist: {dist_x:.1f}m | Pitch: {pitch:.1f}° | State: {fsm.state}")
            
            time.sleep(dt)
            
        print("[MISSION] SUCCESS: Recovery state reached.")
        
    except KeyboardInterrupt:
        print("\n[MISSION] ABORTED by user.")

if __name__ == "__main__":
    main()
