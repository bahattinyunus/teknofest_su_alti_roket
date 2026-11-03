import unittest
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'navigation')))

from acoustic_homing import speed_of_sound_water, AcousticHomingProcessor

class TestAcousticHoming(unittest.TestCase):
    def test_mackenzie_speed_of_sound(self):
        # In typical fresh pool (20°C, 0 ppt): ~1482 m/s
        c_fresh = speed_of_sound_water(temperature_c=20.0, salinity_ppt=0.0, depth_m=1.0)
        self.assertTrue(1475.0 <= c_fresh <= 1490.0)

        # In standard ocean seawater (15°C, 35 ppt): ~1505 m/s
        c_sea = speed_of_sound_water(temperature_c=15.0, salinity_ppt=35.0, depth_m=10.0)
        self.assertTrue(1500.0 <= c_sea <= 1515.0)

    def test_zero_delay_dead_ahead(self):
        processor = AcousticHomingProcessor(baseline_m=0.05, sound_speed_m_s=1482.0)
        # Identical signals on left and right hydrophones
        t = np.linspace(0, 0.001, 250)
        sig = np.sin(2 * np.pi * 30000 * t)

        tdoa = processor.compute_tdoa(sig, sig)
        self.assertAlmostEqual(tdoa, 0.0, places=5)

        bearing = processor.estimate_bearing_2d(sig, sig)
        # Dead ahead = 0 deg relative to vehicle centerline
        self.assertAlmostEqual(bearing, 0.0, delta=1.0)

    def test_delay_bearing_deflection(self):
        processor = AcousticHomingProcessor(baseline_m=0.06, sample_rate_hz=250000.0, sound_speed_m_s=1482.0)
        t = np.linspace(0, 0.002, 500)
        sig = np.sin(2 * np.pi * 30000 * t) * np.exp(-t * 2000)

        # Shift right signal by 5 samples delay (target to the right)
        sig_r = np.roll(sig, 5)
        bearing = processor.estimate_bearing_2d(sig, sig_r)
        self.assertNotEqual(bearing, 0.0)

if __name__ == '__main__':
    unittest.main()
