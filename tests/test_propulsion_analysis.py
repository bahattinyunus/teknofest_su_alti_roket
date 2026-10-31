import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis', 'propulsion')))

from thrust_drag_matching import UnderwaterRocketPropulsion

class TestPropulsionAnalysis(unittest.TestCase):
    def setUp(self):
        self.prop = UnderwaterRocketPropulsion()

    def test_drag_increases_with_velocity(self):
        drag_1ms = self.prop.compute_drag(1.0)["total_drag_n"]
        drag_2ms = self.prop.compute_drag(2.0)["total_drag_n"]
        drag_3ms = self.prop.compute_drag(3.0)["total_drag_n"]

        self.assertGreater(drag_2ms, drag_1ms)
        self.assertGreater(drag_3ms, drag_2ms)
        # Check roughly quadratic scaling (v^2)
        ratio = drag_2ms / drag_1ms
        self.assertTrue(3.2 <= ratio <= 4.2)

    def test_mission_energy_calculation(self):
        m = self.prop.compute_mission_energy(speed_m_s=2.0, distance_m=50.0)
        self.assertEqual(m["transit_time_s"], 25.0)
        self.assertGreater(m["power_electrical_w"], 0.0)
        self.assertGreater(m["energy_consumed_wh"], 0.0)
        self.assertLess(m["battery_pct_used"], 10.0)

if __name__ == '__main__':
    unittest.main()
