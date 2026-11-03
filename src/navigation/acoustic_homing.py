"""
Acoustic Localization & Hydrophone Array Homing for Underwater Vehicles
Implements:
- Mackenzie / Medwin speed of sound calculation in water (f(T, S, Depth))
- Time Difference of Arrival (TDoA) cross-correlation between hydrophone pairs
- Bearing (azimuth) and elevation Angle of Arrival (AoA) estimation
- Multipath reflection rejection for pool wall/surface echoes
"""

import math
import numpy as np
from typing import Dict, Any, List, Tuple

def speed_of_sound_water(temperature_c: float = 20.0,
                         salinity_ppt: float = 0.0, # 0 for pool, ~35 for seawater
                         depth_m: float = 1.5) -> float:
    """
    Computes speed of sound in water using the Mackenzie (1981) empirical formulation.
    Valid for T: 0-30°C, S: 0-40 ppt, D: 0-8000 m.
    """
    t = temperature_c
    s = salinity_ppt
    d = depth_m

    c = (1448.96 +
         4.591 * t -
         5.304e-2 * (t ** 2) +
         2.374e-4 * (t ** 3) +
         1.340 * (s - 35.0) +
         1.630e-2 * d +
         1.675e-7 * (d ** 2) -
         1.025e-2 * t * (s - 35.0) -
         7.139e-13 * t * (d ** 3))
    return float(c)

class AcousticHomingProcessor:
    def __init__(self,
                 baseline_m: float = 0.05, # 50mm distance between hydrophones
                 sample_rate_hz: float = 250000.0, # 250 kHz sampling ADC
                 pinger_freq_hz: float = 30000.0, # 30 kHz acoustic pinger
                 sound_speed_m_s: float = 1482.0):
        self.d = baseline_m
        self.fs = sample_rate_hz
        self.f_ping = pinger_freq_hz
        self.c = sound_speed_m_s

        # Maximum possible delay across baseline (in seconds and samples)
        self.max_tau = self.d / self.c
        self.max_lag_samples = int(math.ceil(self.max_tau * self.fs)) + 2

    def compute_tdoa(self, sig1: np.ndarray, sig2: np.ndarray) -> float:
        """
        Calculates Time Difference of Arrival (TDoA) between two hydrophone channels
        using GCC-PHAT (Generalized Cross Correlation with Phase Transform).
        Returns delta_t in seconds (positive means sig1 arrived before sig2).
        """
        n = len(sig1) + len(sig2)
        # FFT of both signals
        X1 = np.fft.rfft(sig1, n=n)
        X2 = np.fft.rfft(sig2, n=n)

        # Cross-power spectral density
        R12 = X1 * np.conj(X2)
        # Phase transform (whitening)
        R12_phat = R12 / (np.abs(R12) + 1e-9)

        # Inverse FFT to get cross-correlation
        cc = np.fft.irfft(R12_phat, n=n)
        # Shift zero lag to center
        cc = np.concatenate([cc[-(n // 2):], cc[:(n // 2)]])
        center = n // 2

        # Search peak within physical acoustic window
        search_region = cc[center - self.max_lag_samples : center + self.max_lag_samples + 1]
        best_lag_offset = int(np.argmax(search_region)) - self.max_lag_samples

        delta_t = best_lag_offset / self.fs
        return float(delta_t)

    def estimate_bearing_2d(self, sig_left: np.ndarray, sig_right: np.ndarray) -> float:
        """
        Estimates 2D azimuth bearing angle (degrees) relative to vehicle heading:
        0 deg = dead ahead, +90 deg = target to the right, -90 deg = target to the left.
        """
        tau = self.compute_tdoa(sig_left, sig_right)

        # cos(theta) = c * tau / d
        ratio = (self.c * tau) / self.d
        ratio = max(-1.0, min(1.0, ratio)) # Clamp to valid domain

        # Angle relative to baseline axis
        theta_rad = math.acos(ratio)
        # Convert to vehicle forward reference (where 0 deg = normal to baseline)
        bearing_deg = 90.0 - math.degrees(theta_rad)
        return round(bearing_deg, 2)

    def estimate_bearing_triangular_array(self,
                                          sig_a: np.ndarray,
                                          sig_b: np.ndarray,
                                          sig_c: np.ndarray) -> Dict[str, Any]:
        """
        Processes 3 hydrophones mounted in an equilateral triangle.
        Hydrophone A: Nose / Forward
        Hydrophone B: Aft Left
        Hydrophone C: Aft Right
        Returns bearing (0-360 deg) and signal confidence.
        """
        tau_ab = self.compute_tdoa(sig_a, sig_b)
        tau_ac = self.compute_tdoa(sig_a, sig_c)
        tau_bc = self.compute_tdoa(sig_b, sig_c)

        # Consistency check for multipath reflection rejection:
        # tau_ab + tau_bc should approximately equal tau_ac
        closure_error = abs((tau_ab + tau_bc) - tau_ac)
        is_reliable = closure_error < (1.5 / self.fs)

        # Estimate angle
        y_proj = (tau_ac - tau_ab) * math.sqrt(3.0) / 2.0
        x_proj = tau_ac + tau_ab - 2.0 * 0.0

        azimuth = math.atan2(y_proj, x_proj)
        azimuth_deg = (math.degrees(azimuth) + 360.0) % 360.0

        return {
            "bearing_deg": round(azimuth_deg, 1),
            "tau_ab_us": round(tau_ab * 1e6, 2),
            "tau_ac_us": round(tau_ac * 1e6, 2),
            "tau_bc_us": round(tau_bc * 1e6, 2),
            "closure_error_us": round(closure_error * 1e6, 2),
            "is_reliable": is_reliable
        }

if __name__ == "__main__":
    c_pool = speed_of_sound_water(temperature_c=22.0, salinity_ppt=0.0, depth_m=1.5)
    c_sea = speed_of_sound_water(temperature_c=18.0, salinity_ppt=35.0, depth_m=10.0)
    print(f"Speed of sound in fresh pool: {c_pool:.2f} m/s")
    print(f"Speed of sound in sea water:  {c_sea:.2f} m/s")

    processor = AcousticHomingProcessor(baseline_m=0.06, sound_speed_m_s=c_pool)
    # Synthesize sample pings arriving with 20 microsecond delay (target to the right)
    t = np.linspace(0, 0.002, int(250000 * 0.002))
    carrier = np.sin(2 * np.pi * 30000 * t) * np.exp(-t * 2000)
    sig_l = carrier
    delay_samples = 5
    sig_r = np.roll(carrier, delay_samples)

    bearing = processor.estimate_bearing_2d(sig_l, sig_r)
    print(f"Estimated 2D Pinger Bearing: {bearing}°")
