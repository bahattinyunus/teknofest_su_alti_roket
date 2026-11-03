import unittest
import numpy as np
import math
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sim')))

from six_dof_dynamics import SixDoFUnderwaterRocket

class TestSixDoFDynamics(unittest.TestCase):
    def setUp(self):
        self.vehicle = SixDoFUnderwaterRocket()

    def test_initial_state_at_rest(self):
        telem = self.vehicle.get_telemetry()
        self.assertEqual(telem["x_m"], 0.0)
        self.assertEqual(telem["depth_m"], 0.0)
        self.assertEqual(telem["u_surge_m_s"], 0.0)

    def test_forward_thrust_produces_positive_surge(self):
        dt = 0.02
        fins = np.zeros(4)
        for _ in range(50): # 1.0 second
            self.vehicle.step(dt=dt, thrust_n=25.0, fin_angles_deg=fins)

        telem = self.vehicle.get_telemetry()
        self.assertGreater(telem["u_surge_m_s"], 0.5)
        self.assertGreater(telem["x_m"], 0.2)

    def test_restoring_moments_pitch_stability(self):
        # Set pitch angle to +20 degrees (nose up)
        self.vehicle.eta[4] = math.radians(20.0)
        restoring = self.vehicle.restoring_forces()
        # Pitch restoring moment (index 4) should oppose positive pitch
        self.assertGreater(restoring[4], 0.0)

    def test_surface_boundary_condition(self):
        # Even with upwards vertical velocity, vehicle depth should not go negative
        self.vehicle.eta[2] = 0.0
        self.vehicle.nu[2] = -1.0 # upward velocity
        self.vehicle.step(dt=0.05, thrust_n=0.0, fin_angles_deg=np.zeros(4))
        self.assertGreaterEqual(self.vehicle.eta[2], 0.0)

if __name__ == '__main__':
    unittest.main()
