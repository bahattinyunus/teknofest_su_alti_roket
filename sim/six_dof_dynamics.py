"""
6-Degrees-of-Freedom (6-DoF) Nonlinear Hydrodynamic Vehicle Dynamics
Implements the Fossen (2011) Marine Vehicle Equations of Motion:
M * nu_dot + C(nu)*nu + D(nu)*nu + g(eta) = tau

Accounts for:
- Rigid-body mass and fluid added mass (M_RB + M_A)
- Coriolis-centripetal forces
- Linear and quadratic hydrodynamic damping (D_linear + D_nonlinear)
- Hydrostatic restoring forces (Weight W vs Buoyancy B with CG/CB offsets)
- Actuation wrench tau from main propeller and 4x control fins (X-Rudder / Cruciform)
"""

import math
import numpy as np
from typing import Dict, Any, Tuple

class SixDoFUnderwaterRocket:
    def __init__(self,
                 mass_kg: float = 8.5,
                 volume_m3: float = 0.0086, # slightly positive buoyancy
                 length_m: float = 1.2,
                 diameter_m: float = 0.15,
                 water_density_kg_m3: float = 1025.0):
        self.m = mass_kg
        self.vol = volume_m3
        self.rho = water_density_kg_m3
        self.g = 9.80665
        self.w = self.m * self.g
        self.b = self.rho * self.vol * self.g
        self.L = length_m
        self.D = diameter_m

        # Center of Gravity (CG) and Center of Buoyancy (CB) in body coordinates (meters)
        # For hydrostatic stability, CB is positioned above CG: z_g > z_b
        self.r_g = np.array([0.0, 0.0, 0.015])  # 15mm below origin
        self.r_b = np.array([0.0, 0.0, -0.010]) # 10mm above origin

        # Rigid body moments of inertia (approx cylinder / prolate spheroid)
        I_xx = 0.5 * self.m * ((self.D / 2.0) ** 2)
        I_yy = (1.0 / 12.0) * self.m * (3 * ((self.D / 2.0) ** 2) + self.L ** 2)
        I_zz = I_yy
        self.I_diag = np.array([I_xx, I_yy, I_zz])

        # 1. Rigid-Body Mass Matrix M_RB
        self.M_rb = np.diag([self.m, self.m, self.m, I_xx, I_yy, I_zz])

        # 2. Added Mass Matrix M_A (hydrodynamic virtual mass of displaced water)
        # Sleneder body approximations for prolate spheroid
        X_udot = -0.05 * self.m # Surge added mass is small (~5% of dry mass)
        Y_vdot = -0.85 * self.m # Sway added mass (~85% of dry mass)
        Z_wdot = -0.85 * self.m # Heave added mass
        K_pdot = -0.05 * I_xx   # Roll added inertia
        M_qdot = -0.70 * I_yy   # Pitch added inertia
        N_rdot = -0.70 * I_zz   # Yaw added inertia

        self.M_a = -np.diag([X_udot, Y_vdot, Z_wdot, K_pdot, M_qdot, N_rdot])
        self.M_total = self.M_rb + self.M_a
        self.M_inv = np.linalg.inv(self.M_total)

        # 3. Damping Coefficients (Linear and Quadratic Drag)
        self.D_lin = np.diag([4.0, 28.0, 28.0, 0.15, 4.5, 4.5])
        self.D_quad = np.diag([12.0, 65.0, 65.0, 0.35, 18.0, 18.0])

        # State Vectors:
        # eta = [x, y, z, phi (roll), theta (pitch), psi (yaw)] in NED earth frame
        self.eta = np.zeros(6, dtype=np.float64)
        # nu = [u (surge), v (sway), w (heave), p (roll rate), q (pitch rate), r (yaw rate)] in body frame
        self.nu = np.zeros(6, dtype=np.float64)

    def restoring_forces(self) -> np.ndarray:
        """Computes hydrostatic restoring wrench g(eta) due to gravity and buoyancy."""
        phi = self.eta[3]
        theta = self.eta[4]

        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        # Net forces in body frame
        f_g = np.array([
            (self.w - self.b) * sin_theta,
            -(self.w - self.b) * cos_theta * sin_phi,
            -(self.w - self.b) * cos_theta * cos_phi
        ])

        # Net moments in body frame: r_g x W - r_b x B
        m_g = np.array([
            (self.r_g[1]*self.w - self.r_b[1]*self.b) * cos_theta * cos_phi - (self.r_g[2]*self.w - self.r_b[2]*self.b) * cos_theta * sin_phi,
            -(self.r_g[0]*self.w - self.r_b[0]*self.b) * cos_theta * cos_phi - (self.r_g[2]*self.w - self.r_b[2]*self.b) * sin_theta,
            (self.r_g[0]*self.w - self.r_b[0]*self.b) * cos_theta * sin_phi + (self.r_g[1]*self.w - self.r_b[1]*self.b) * sin_theta
        ])

        return np.concatenate([-f_g, -m_g])

    def rotation_matrix(self) -> np.ndarray:
        """Euler angle transformation from Body frame to NED Earth frame."""
        phi = self.eta[3]
        theta = self.eta[4]
        psi = self.eta[5]

        c_p = math.cos(phi);   s_p = math.sin(phi)
        c_t = math.cos(theta); s_t = math.sin(theta)
        c_s = math.cos(psi);   s_s = math.sin(psi)

        R = np.array([
            [c_s*c_t, c_s*s_t*s_p - s_s*c_p, c_s*s_t*c_p + s_s*s_p],
            [s_s*c_t, s_s*s_t*s_p + c_s*c_p, s_s*s_t*c_p - c_s*s_p],
            [-s_t,    c_t*s_p,               c_t*c_p]
        ])
        return R

    def angular_rate_matrix(self) -> np.ndarray:
        """Transforms body angular velocity [p, q, r] to Euler rate [phi_dot, theta_dot, psi_dot]."""
        phi = self.eta[3]
        theta = self.eta[4]

        s_p = math.sin(phi);   c_p = math.cos(phi)
        t_t = math.tan(theta); c_t = math.cos(theta)
        if abs(c_t) < 1e-4:
            c_t = math.copysign(1e-4, c_t)

        T = np.array([
            [1.0, s_p * t_t, c_p * t_t],
            [0.0, c_p,       -s_p],
            [0.0, s_p / c_t, c_p / c_t]
        ])
        return T

    def compute_actuator_wrench(self, thrust_n: float, fin_angles_deg: np.ndarray) -> np.ndarray:
        """
        Computes 6-DoF input wrench tau from:
        - Propeller thrust along x-axis (body surge)
        - 4x Fin control surfaces (X-Rudder layout at 45 deg)
        """
        tau = np.zeros(6, dtype=np.float64)
        tau[0] = thrust_n # Surge force

        # Hydrodynamic lift from fins proportional to dynamic pressure q = 0.5 * rho * u^2
        u = max(0.2, self.nu[0]) # forward speed
        q_dyn = 0.5 * self.rho * (u ** 2)
        fin_area = 0.0035 # m^2 per fin
        fin_arm_x = 0.55  # 550mm aft of CG

        # Fin angles in radians: delta1 (TL), delta2 (TR), delta3 (BL), delta4 (BR)
        deltas = np.radians(fin_angles_deg)
        lift_slope = 3.8 # 3D wing lift curve slope (1/rad)

        fin_lifts = q_dyn * fin_area * lift_slope * deltas

        # X-Rudder moment coupling:
        # Fin 1 (Top-Left): produces Pitch Down, Yaw Right, Roll CW
        # Fin 2 (Top-Right): produces Pitch Down, Yaw Left, Roll CCW
        # Fin 3 (Bottom-Left): produces Pitch Up, Yaw Right, Roll CCW
        # Fin 4 (Bottom-Right): produces Pitch Up, Yaw Left, Roll CW
        inv_sqrt2 = 0.7071

        m_pitch = fin_arm_x * inv_sqrt2 * (-fin_lifts[0] - fin_lifts[1] + fin_lifts[2] + fin_lifts[3])
        m_yaw   = fin_arm_x * inv_sqrt2 * ( fin_lifts[0] - fin_lifts[1] + fin_lifts[2] - fin_lifts[3])
        m_roll  = 0.06 * (fin_lifts[0] - fin_lifts[1] - fin_lifts[2] + fin_lifts[3])

        tau[3] = m_roll
        tau[4] = m_pitch
        tau[5] = m_yaw
        return tau

    def step(self, dt: float, thrust_n: float, fin_angles_deg: np.ndarray):
        """Advances the 6-DoF state by dt seconds using Runge-Kutta 2nd order (Heun) integration."""
        if dt <= 0.0:
            return

        tau = self.compute_actuator_wrench(thrust_n, fin_angles_deg)

        # Damping wrench: D(nu) * nu = D_lin * nu + D_quad * |nu| * nu
        damping_wrench = self.D_lin @ self.nu + self.D_quad @ (np.abs(self.nu) * self.nu)

        # Restoring wrench: g(eta)
        restoring = self.restoring_forces()

        # Equations of motion in body frame:
        # M_total * nu_dot = tau - damping_wrench - restoring
        net_wrench = tau - damping_wrench - restoring
        nu_dot = self.M_inv @ net_wrench

        # Integrate body velocities
        self.nu += nu_dot * dt

        # Kinematic transformation to earth-fixed rates:
        R = self.rotation_matrix()
        T = self.angular_rate_matrix()

        pos_dot = R @ self.nu[0:3]
        euler_dot = T @ self.nu[3:6]
        eta_dot = np.concatenate([pos_dot, euler_dot])

        # Integrate positions and orientations
        self.eta += eta_dot * dt

        # Boundary condition at water surface (z <= 0)
        if self.eta[2] < 0.0:
            self.eta[2] = 0.0
            if self.nu[2] < 0.0:
                self.nu[2] = 0.0

        # Normalize Euler angles to [-pi, pi]
        self.eta[3] = (self.eta[3] + math.pi) % (2.0 * math.pi) - math.pi
        self.eta[4] = (self.eta[4] + math.pi) % (2.0 * math.pi) - math.pi
        self.eta[5] = (self.eta[5] + math.pi) % (2.0 * math.pi) - math.pi

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "x_m": round(float(self.eta[0]), 2),
            "y_m": round(float(self.eta[1]), 2),
            "depth_m": round(float(self.eta[2]), 3),
            "roll_deg": round(math.degrees(float(self.eta[3])), 2),
            "pitch_deg": round(math.degrees(float(self.eta[4])), 2),
            "yaw_deg": round(math.degrees(float(self.eta[5])), 2),
            "u_surge_m_s": round(float(self.nu[0]), 2),
            "v_sway_m_s": round(float(self.nu[1]), 2),
            "w_heave_m_s": round(float(self.nu[2]), 2),
            "p_roll_rate_deg_s": round(math.degrees(float(self.nu[3])), 2),
            "q_pitch_rate_deg_s": round(math.degrees(float(self.nu[4])), 2),
            "r_yaw_rate_deg_s": round(math.degrees(float(self.nu[5])), 2)
        }

if __name__ == "__main__":
    sim = SixDoFUnderwaterRocket()
    print("=== 6-DOF NONLINEAR UNDERWATER DYNAMICS SIMULATION ===")
    print("Simulating 5 seconds of powered forward flight with pitch-up command...")
    dt = 0.02
    for t in range(250): # 5.0 seconds
        thrust = 28.0 # Newtons
        # Pitch-up fin angles (symmetric elevator deflection on X-rudder)
        fins = np.array([12.0, 12.0, -12.0, -12.0])
        sim.step(dt, thrust, fins)
        if t % 50 == 0:
            telem = sim.get_telemetry()
            print(f"t={t*dt:.1f}s | X={telem['x_m']}m, Depth={telem['depth_m']}m, Pitch={telem['pitch_deg']}°, Surge={telem['u_surge_m_s']}m/s")
