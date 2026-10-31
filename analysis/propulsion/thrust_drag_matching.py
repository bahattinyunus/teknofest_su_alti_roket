"""
Propulsion and Hydrodynamic Drag Matching Analysis for Underwater Rocket
Calculates hull resistance using ITTC-1957 skin friction line, form factor,
and matches propeller thrust, motor electrical power, and battery runtime.
"""

import math
from typing import Dict, Any, List

class UnderwaterRocketPropulsion:
    def __init__(self,
                 length_m: float = 1.2,
                 diameter_m: float = 0.15,
                 mass_kg: float = 8.5,
                 water_density_kg_m3: float = 1025.0, # Seawater
                 kinematic_viscosity: float = 1.05e-6, # m^2/s at 20°C
                 propeller_efficiency: float = 0.55,
                 motor_efficiency: float = 0.82,
                 battery_voltage_v: float = 14.8, # 4S Li-Po
                 battery_capacity_mah: float = 5000.0):
        self.length = length_m
        self.diameter = diameter_m
        self.mass = mass_kg
        self.rho = water_density_kg_m3
        self.nu = kinematic_viscosity
        self.eta_prop = propeller_efficiency
        self.eta_motor = motor_efficiency
        self.voltage = battery_voltage_v
        self.battery_capacity_ah = battery_capacity_mah / 1000.0

        # Wetted surface area approximation for streamlined torpedo (Myring profile)
        self.frontal_area = math.pi * ((self.diameter / 2.0) ** 2)
        # Approximate wetted area ~ pi * D * L * 0.75
        self.wetted_area = math.pi * self.diameter * self.length * 0.78
        self.slenderness_ratio = self.length / self.diameter # L / D

    def compute_drag(self, velocity_m_s: float) -> Dict[str, float]:
        if velocity_m_s <= 0.0:
            return {"total_drag_n": 0.0, "power_thrust_w": 0.0, "power_electrical_w": 0.0, "reynolds": 0.0}

        # 1. Reynolds Number: Re = V * L / nu
        re = (velocity_m_s * self.length) / self.nu

        # 2. ITTC-1957 Friction Line: Cf = 0.075 / (log10(Re) - 2)^2
        log_re = math.log10(re)
        cf = 0.075 / ((log_re - 2.0) ** 2)

        # 3. Form factor (1 + k) via Hoerner empirical formulation for streamlined bodies:
        # (1 + k) = 1 + 1.5 * (D/L)^1.5 + 7 * (D/L)^3
        d_over_l = self.diameter / self.length
        form_factor = 1.0 + 1.5 * (d_over_l ** 1.5) + 7.0 * (d_over_l ** 3.0)

        # 4. Appendage & Fin Drag Allowance (+15% of bare hull drag)
        appendage_factor = 1.15

        # 5. Total Drag Coefficient based on wetted area
        cd_wet = cf * form_factor * appendage_factor
        total_drag_n = 0.5 * self.rho * (velocity_m_s ** 2) * self.wetted_area * cd_wet

        # 6. Drag Coefficient based on frontal area (for standard comparison)
        cd_frontal = total_drag_n / (0.5 * self.rho * (velocity_m_s ** 2) * self.frontal_area)

        # 7. Required Thrust Power (effective tow power): P_e = Drag * V
        power_thrust_w = total_drag_n * velocity_m_s

        # 8. Total Electrical Power: P_elec = P_e / (eta_prop * eta_motor)
        combined_efficiency = self.eta_prop * self.eta_motor
        power_electrical_w = power_thrust_w / combined_efficiency

        # 9. Current Draw (Amperes)
        current_a = power_electrical_w / self.voltage

        return {
            "velocity_m_s": round(velocity_m_s, 2),
            "reynolds": round(re, 0),
            "skin_friction_cf": round(cf, 5),
            "cd_frontal": round(cd_frontal, 3),
            "total_drag_n": round(total_drag_n, 2),
            "thrust_required_n": round(total_drag_n, 2),
            "power_thrust_w": round(power_thrust_w, 2),
            "power_electrical_w": round(power_electrical_w, 2),
            "current_a": round(current_a, 2)
        }

    def compute_mission_energy(self, speed_m_s: float, distance_m: float) -> Dict[str, Any]:
        drag_info = self.compute_drag(speed_m_s)
        time_s = distance_m / speed_m_s if speed_m_s > 0 else 0.0

        # Energy consumed in Watt-hours
        energy_wh = (drag_info["power_electrical_w"] * time_s) / 3600.0
        # Battery capacity used in mAh
        capacity_used_mah = (drag_info["current_a"] * (time_s / 3600.0)) * 1000.0
        battery_pct_used = (capacity_used_mah / (self.battery_capacity_ah * 1000.0)) * 100.0

        return {
            "mission_distance_m": distance_m,
            "cruise_speed_m_s": speed_m_s,
            "transit_time_s": round(time_s, 1),
            "power_electrical_w": drag_info["power_electrical_w"],
            "current_a": drag_info["current_a"],
            "energy_consumed_wh": round(energy_wh, 2),
            "capacity_used_mah": round(capacity_used_mah, 1),
            "battery_pct_used": round(battery_pct_used, 1),
            "battery_remaining_pct": round(max(0.0, 100.0 - battery_pct_used), 1)
        }

    def generate_speed_sweep(self, v_min: float = 0.5, v_max: float = 4.0, steps: int = 8) -> List[Dict[str, float]]:
        results = []
        step_size = (v_max - v_min) / (steps - 1)
        for i in range(steps):
            v = v_min + i * step_size
            results.append(self.compute_drag(v))
        return results

if __name__ == "__main__":
    prop = UnderwaterRocketPropulsion()
    print("=== PROPULSION & DRAG SWEEP ANALYSIS ===")
    sweep = prop.generate_speed_sweep()
    for pt in sweep:
        print(f"V: {pt['velocity_m_s']} m/s | Drag: {pt['total_drag_n']} N | P_elec: {pt['power_electrical_w']} W | Current: {pt['current_a']} A | Cd: {pt['cd_frontal']}")

    print("\n=== MISSION 1 (50m Out + 50m Return = 100m at 2.5 m/s) ===")
    m1 = prop.compute_mission_energy(speed_m_s=2.5, distance_m=100.0)
    for k, v in m1.items():
        print(f"  {k}: {v}")
