"""
Structural Analysis and Wall Thickness Verification for Subsea Pressure Hull
Calculates hydrostatic pressure, hoop and longitudinal stresses, von Mises stress,
and critical buckling collapse pressure for various materials (Acrylic, 6061-T6 Aluminum, Polycarbonate).
"""

import math
from typing import Dict, Any

MATERIAL_DATABASE = {
    "ACRYLIC_PMMA": {
        "name": "Cast Acrylic (PMMA)",
        "youngs_modulus_gpa": 3.1,
        "poisson_ratio": 0.37,
        "yield_strength_mpa": 65.0,
        "density_kg_m3": 1180.0
    },
    "POLYCARBONATE": {
        "name": "Polycarbonate (Lexan)",
        "youngs_modulus_gpa": 2.4,
        "poisson_ratio": 0.38,
        "yield_strength_mpa": 62.0,
        "density_kg_m3": 1200.0
    },
    "ALUMINUM_6061_T6": {
        "name": "Aluminum 6061-T6",
        "youngs_modulus_gpa": 68.9,
        "poisson_ratio": 0.33,
        "yield_strength_mpa": 276.0,
        "density_kg_m3": 2700.0
    }
}

class SubseaHullAnalysis:
    def __init__(self,
                 outer_diameter_mm: float = 150.0,
                 wall_thickness_mm: float = 5.0,
                 unsupported_length_mm: float = 600.0,
                 material_key: str = "ACRYLIC_PMMA"):
        self.d_outer = outer_diameter_mm / 1000.0 # meters
        self.t = wall_thickness_mm / 1000.0       # meters
        self.length = unsupported_length_mm / 1000.0 # meters
        self.d_inner = self.d_outer - 2.0 * self.t
        self.d_mean = (self.d_outer + self.d_inner) / 2.0

        if material_key not in MATERIAL_DATABASE:
            material_key = "ACRYLIC_PMMA"
        self.mat = MATERIAL_DATABASE[material_key]
        self.e_pa = self.mat["youngs_modulus_gpa"] * 1e9
        self.nu = self.mat["poisson_ratio"]
        self.sigma_y_pa = self.mat["yield_strength_mpa"] * 1e6

    def compute_safety_at_depth(self, depth_m: float = 10.0) -> Dict[str, Any]:
        # Hydrostatic Gauge Pressure: P_gauge = rho * g * h
        rho_water = 1025.0 # kg/m^3
        g = 9.80665
        p_gauge_pa = rho_water * g * depth_m
        p_gauge_bar = p_gauge_pa / 1e5

        # 1. Thin-wall / Mean diameter stress approximations
        # Hoop (circumferential) stress: sigma_h = P * D_mean / (2 * t)
        sigma_hoop_pa = (p_gauge_pa * self.d_mean) / (2.0 * self.t)
        sigma_hoop_mpa = sigma_hoop_pa / 1e6

        # Longitudinal (axial) stress: sigma_l = P * D_mean / (4 * t)
        sigma_long_pa = (p_gauge_pa * self.d_mean) / (4.0 * self.t)
        sigma_long_mpa = sigma_long_pa / 1e6

        # von Mises equivalent stress: sigma_vm = sqrt(sigma_h^2 - sigma_h * sigma_l + sigma_l^2)
        sigma_vm_pa = math.sqrt(sigma_hoop_pa**2 - sigma_hoop_pa * sigma_long_pa + sigma_long_pa**2)
        sigma_vm_mpa = sigma_vm_pa / 1e6

        # Yield Factor of Safety
        fos_yield = self.sigma_y_pa / (sigma_vm_pa + 1e-6)

        # 2. Critical Buckling Collapse Pressure (Windenburg / Southwell formula for subsea cylinders)
        # P_cr = (2.42 * E * (t / D_mean)^2.5) / ((1 - nu^2)^0.75 * (L / D_mean - 0.45 * sqrt(t / D_mean)))
        t_over_d = self.t / self.d_mean
        l_over_d = self.length / self.d_mean

        denominator = ((1.0 - self.nu**2)**0.75) * (l_over_d - 0.45 * math.sqrt(t_over_d))
        if denominator > 0:
            p_buckling_pa = (2.42 * self.e_pa * (t_over_d**2.5)) / denominator
            p_buckling_bar = p_buckling_pa / 1e5
            max_depth_buckling_m = p_buckling_pa / (rho_water * g)
            fos_buckling = p_buckling_pa / (p_gauge_pa + 1e-6)
        else:
            p_buckling_bar = 999.0
            max_depth_buckling_m = 999.0
            fos_buckling = 999.0

        is_safe = (fos_yield >= 2.0) and (fos_buckling >= 2.5)

        return {
            "material": self.mat["name"],
            "depth_tested_m": depth_m,
            "hydrostatic_pressure_bar": round(p_gauge_bar, 3),
            "hoop_stress_mpa": round(sigma_hoop_mpa, 2),
            "longitudinal_stress_mpa": round(sigma_long_mpa, 2),
            "von_mises_stress_mpa": round(sigma_vm_mpa, 2),
            "fos_yield": round(fos_yield, 2),
            "critical_buckling_pressure_bar": round(p_buckling_bar, 2),
            "max_collapse_depth_m": round(max_depth_buckling_m, 1),
            "fos_buckling": round(fos_buckling, 2),
            "structural_status": "PASSED (SAFE)" if is_safe else "WARNING (LOW SAFETY FACTOR)"
        }

if __name__ == "__main__":
    print("=== SUBSEA PRESSURE HULL STRUCTURAL VERIFICATION ===")
    for mat_key in ["ACRYLIC_PMMA", "POLYCARBONATE", "ALUMINUM_6061_T6"]:
        analysis = SubseaHullAnalysis(outer_diameter_mm=150.0, wall_thickness_mm=5.0, unsupported_length_mm=600.0, material_key=mat_key)
        res = analysis.compute_safety_at_depth(depth_m=10.0)
        print(f"\nMaterial: {res['material']} at {res['depth_tested_m']}m Depth")
        print(f"  Hydrostatic Pressure: {res['hydrostatic_pressure_bar']} bar")
        print(f"  von Mises Stress: {res['von_mises_stress_mpa']} MPa | FOS Yield: {res['fos_yield']}")
        print(f"  Buckling Pressure: {res['critical_buckling_pressure_bar']} bar | Max Depth: {res['max_collapse_depth_m']} m | FOS Buckling: {res['fos_buckling']}")
        print(f"  Status: {res['structural_status']}")
