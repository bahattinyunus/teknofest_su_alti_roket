"""
Mission Simulator for TEKNOFEST Autonomous Underwater Rocket Teams
Simulates torpedic hydrodynamics, fin control surface response, and mission state sequencing.
"""

import math
from typing import Dict, List

class UnderwaterRocketDynamics:
    def __init__(self):
        # Physical parameters
        self.mass = 8.5 # kg
        self.volume = 0.0086 # m^3 (approx neutral / slight positive)
        self.rho_water = 1025.0 # kg/m^3 (seawater)
        self.g = 9.80665
        self.drag_cd = 0.18 # hydrodynamic drag coefficient for streamlined torpedo
        self.frontal_area = math.pi * (0.075 ** 2) # 150mm diameter

        # States
        self.x = 0.0 # forward distance (m)
        self.z = 0.0 # depth positive downward (m)
        self.vx = 0.0 # surge velocity (m/s)
        self.vz = 0.0 # heave velocity (m/s)
        self.pitch = 0.0 # degrees (- = nose down, + = nose up)
        self.pitch_rate = 0.0 # deg/s
        self.heading = 0.0 # degrees

    def step(self, dt: float, thrust: float, fin_pitch_angle: float, fin_yaw_rate: float = 0.0):
        # Hydrodynamic pitch damping
        pitch_moment = fin_pitch_angle * 12.0 - self.pitch_rate * 4.0
        self.pitch_rate += pitch_moment * dt
        self.pitch += self.pitch_rate * dt
        self.pitch = max(-45.0, min(45.0, self.pitch))

        # Heading integration
        self.heading = (self.heading + fin_yaw_rate * dt) % 360.0

        # Surge & Heave kinematics
        pitch_rad = math.radians(self.pitch)
        heading_rad = math.radians(self.heading)

        # Forward thrust projection
        speed = 2.2 if thrust > 0 else 0.0
        self.vx = speed * math.cos(heading_rad)
        self.vz = -speed * math.sin(pitch_rad)

        self.x += self.vx * dt
        self.z += self.vz * dt
        if self.z < 0.0:
            self.z = 0.0
            self.vz = 0.0

    def get_state(self) -> Dict[str, float]:
        return {
            "x": round(self.x, 2),
            "depth": round(self.z, 3),
            "vx": round(self.vx, 2),
            "vz": round(self.vz, 2),
            "pitch": round(self.pitch, 2),
            "heading": round(self.heading, 1)
        }

class MissionSimulator:
    def __init__(self, mode: int = 1):
        self.mode = mode # 1 = Seyir & Donus, 2 = Yunuslama & Roket Atesleme
        self.dynamics = UnderwaterRocketDynamics()
        self.target_depth = 1.5 # meters
        self.time_elapsed = 0.0
        self.log: List[Dict[str, float]] = []

    def run(self, max_duration: float = 60.0, dt: float = 0.05) -> bool:
        completed = False
        stage = "DIVE"

        while self.time_elapsed < max_duration:
            state = self.dynamics.get_state()
            thrust = 25.0
            fin_pitch = 0.0
            fin_yaw_rate = 0.0

            if self.mode == 1:
                # Stage 1: Dive to 1.5m, cruise to 50m, 180 turn, return to 0m
                if stage == "DIVE":
                    depth_err = self.target_depth - state["depth"]
                    fin_pitch = -depth_err * 8.0 # dive nose down
                    if state["depth"] >= 1.3:
                        stage = "CRUISE_50M"

                elif stage == "CRUISE_50M":
                    depth_err = self.target_depth - state["depth"]
                    fin_pitch = -depth_err * 6.0
                    if state["x"] >= 50.0:
                        stage = "TURN_180"

                elif stage == "TURN_180":
                    fin_yaw_rate = 45.0 # deg/sec yaw turn
                    depth_err = self.target_depth - state["depth"]
                    fin_pitch = -depth_err * 5.0
                    if 170.0 <= state["heading"] <= 190.0:
                        stage = "RETURN"

                elif stage == "RETURN":
                    depth_err = self.target_depth - state["depth"]
                    fin_pitch = -depth_err * 5.0
                    if state["x"] <= 1.0:
                        thrust = 0.0
                        stage = "COMPLETE"
                        completed = True
                        break

            elif self.mode == 2:
                # Stage 2: Dive, cruise 30m, pitch-up (yunuslama), surface & launch
                if stage == "DIVE":
                    depth_err = self.target_depth - state["depth"]
                    fin_pitch = -depth_err * 8.0
                    if state["depth"] >= 1.3:
                        stage = "CRUISE_30M"

                elif stage == "CRUISE_30M":
                    depth_err = self.target_depth - state["depth"]
                    fin_pitch = -depth_err * 6.0
                    if state["x"] >= 30.0:
                        stage = "YUNUSLAMA_PITCH_UP"

                elif stage == "YUNUSLAMA_PITCH_UP":
                    fin_pitch = 25.0 # aggressive pitch up to surface
                    if state["depth"] <= 0.1:
                        stage = "SURFACE_LAUNCH"

                elif stage == "SURFACE_LAUNCH":
                    thrust = 0.0
                    stage = "COMPLETE"
                    completed = True
                    break

            self.dynamics.step(dt, thrust, fin_pitch, fin_yaw_rate)
            self.time_elapsed += dt

            entry = {"t": round(self.time_elapsed, 2), "stage": stage}
            entry.update(self.dynamics.get_state())
            self.log.append(entry)

        return completed

if __name__ == "__main__":
    sim1 = MissionSimulator(mode=1)
    res1 = sim1.run()
    print(f"Mission 1 Completed: {res1} in {sim1.time_elapsed:.1f}s, Final State: {sim1.dynamics.get_state()}")

    sim2 = MissionSimulator(mode=2)
    res2 = sim2.run()
    print(f"Mission 2 Completed: {res2} in {sim2.time_elapsed:.1f}s, Final State: {sim2.dynamics.get_state()}")
