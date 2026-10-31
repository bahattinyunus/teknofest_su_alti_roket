"""
Fin Aerodynamic & Hydrodynamic Lift-Drag Polar and Servo Torque Calculator
Models symmetric hydrofoils (NACA 0012/0015) for underwater rocket control surfaces.
Verifies control authority, stall angle, and required servo torque margins.
"""

import math
from typing import Dict, Any, List

class ControlFinHydrodynamics:
    def __init__(self,
                 span_m: float = 0.08, # 80mm span
                 chord_root_m: float = 0.07, # 70mm root chord
                 chord_tip_m: float = 0.04,  # 40mm tip chord
                 thickness_ratio: float = 0.12, # NACA 0012
                 hinge_axis_fraction: float = 0.28, # Hinge positioned at 28% chord from leading edge
                 water_density_kg_m3: float = 1025.0):
        self.span = span_m
        self.chord_root = chord_root_m
        self.chord_tip = chord_tip_m
        self.mean_chord = (self.chord_root + self.chord_tip) / 2.0
        self.planform_area = self.span * self.mean_chord # m^2
        self.aspect_ratio = (self.span ** 2) / self.planform_area
        self.hinge_frac = hinge_axis_fraction
        self.rho = water_density_kg_m3
        self.cd0 = 0.008 + 0.01 * (thickness_ratio / 0.12) # Profile minimum drag
        self.oswald_eff = 0.85 # Span efficiency factor

    def compute_fin_performance(self, angle_of_attack_deg: float, velocity_m_s: float) -> Dict[str, Any]:
        aoa_rad = math.radians(angle_of_attack_deg)

        # 3D Finite Wing Lift Curve Slope: a = a0 / (1 + a0 / (pi * e * AR))
        a0 = 2.0 * math.pi # 2D theoretical slope ~ 6.28 / rad
        lift_slope = a0 / (1.0 + a0 / (math.pi * self.oswald_eff * self.aspect_ratio))

        # Stall modeling (linear up to 14 deg, softens, stalls past 16 deg)
        abs_aoa = abs(angle_of_attack_deg)
        if abs_aoa <= 14.0:
            cl = lift_slope * aoa_rad
        elif abs_aoa <= 18.0:
            # Post-stall transition
            cl_max = lift_slope * math.radians(14.0)
            cl = math.copysign(cl_max * (1.0 - 0.2 * ((abs_aoa - 14.0) / 4.0)), angle_of_attack_deg)
        else:
            cl = math.copysign(0.8 * math.sin(2.0 * aoa_rad), angle_of_attack_deg)

        # Drag Polar: Cd = Cd0 + Cl^2 / (pi * e * AR)
        cd_induced = (cl ** 2) / (math.pi * self.oswald_eff * self.aspect_ratio)
        cd_total = self.cd0 + cd_induced

        # Dynamic Pressure: q = 0.5 * rho * V^2
        q = 0.5 * self.rho * (velocity_m_s ** 2)

        # Forces on single fin
        lift_force_n = q * self.planform_area * cl
        drag_force_n = q * self.planform_area * cd_total

        # Aerodynamic center is at approx 25% chord.
        # Hinge moment arm = (hinge_position - 0.25) * mean_chord
        moment_arm_m = abs(self.hinge_frac - 0.25) * self.mean_chord
        hinge_torque_nm = abs(lift_force_n) * moment_arm_m
        hinge_torque_kg_cm = (hinge_torque_nm / 9.80665) * 100.0

        return {
            "aoa_deg": round(angle_of_attack_deg, 1),
            "velocity_m_s": round(velocity_m_s, 2),
            "lift_coefficient_cl": round(cl, 3),
            "drag_coefficient_cd": round(cd_total, 4),
            "lift_force_n": round(lift_force_n, 2),
            "drag_force_n": round(drag_force_n, 2),
            "hinge_torque_nm": round(hinge_torque_nm, 3),
            "hinge_torque_kg_cm": round(hinge_torque_kg_cm, 2),
            "is_stalled": abs_aoa > 15.0
        }

    def generate_polar(self, velocity_m_s: float = 2.5) -> List[Dict[str, Any]]:
        polar = []
        for aoa in range(-20, 22, 2):
            polar.append(self.compute_fin_performance(float(aoa), velocity_m_s))
        return polar

if __name__ == "__main__":
    fin = ControlFinHydrodynamics()
    print("=== CONTROL FIN HYDRODYNAMIC POLAR AT V = 2.5 m/s ===")
    polar = fin.generate_polar(velocity_m_s=2.5)
    for p in polar:
        if p["aoa_deg"] in [0.0, 5.0, 10.0, 15.0, 20.0]:
            print(f"AoA: {p['aoa_deg']:>4}° | Cl: {p['lift_coefficient_cl']:>5} | Cd: {p['drag_coefficient_cd']:>6} | Lift: {p['lift_force_n']:>5} N | Torque: {p['hinge_torque_kg_cm']} kg.cm | Stall: {p['is_stalled']}")
