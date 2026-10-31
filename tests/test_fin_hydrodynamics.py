import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis', 'cfd')))

from fin_lift_drag_polar import ControlFinHydrodynamics

class TestFinHydrodynamics(unittest.TestCase):
    def setUp(self):
        self.fin = ControlFinHydrodynamics()

    def test_zero_aoa_symmetric_polar(self):
        p0 = self.fin.compute_fin_performance(0.0, 2.5)
        self.assertEqual(p0["lift_coefficient_cl"], 0.0)
        self.assertEqual(p0["lift_force_n"], 0.0)
        self.assertGreater(p0["drag_force_n"], 0.0)

    def test_positive_aoa_lift_and_torque(self):
        p10 = self.fin.compute_fin_performance(10.0, 2.5)
        self.assertGreater(p10["lift_coefficient_cl"], 0.0)
        self.assertGreater(p10["lift_force_n"], 5.0)
        self.assertGreater(p10["hinge_torque_kg_cm"], 0.0)
        # Verify typical micro servo (< 2 kg.cm) can handle this torque
        self.assertLess(p10["hinge_torque_kg_cm"], 2.5)

    def test_stall_detection(self):
        p20 = self.fin.compute_fin_performance(20.0, 2.5)
        self.assertTrue(p20["is_stalled"])

if __name__ == '__main__':
    unittest.main()
