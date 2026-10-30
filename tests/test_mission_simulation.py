import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sim')))

from mission_simulator import MissionSimulator

class TestMissionSimulator(unittest.TestCase):
    def test_mission_1_cruise_and_return(self):
        sim = MissionSimulator(mode=1)
        completed = sim.run(max_duration=65.0)
        self.assertTrue(completed, "Stage 1 cruise (50m), turn (180 deg) and return should complete successfully.")
        self.assertLess(sim.time_elapsed, 60.0)
        self.assertLessEqual(sim.dynamics.x, 2.0)

    def test_mission_2_surface_and_launch(self):
        sim = MissionSimulator(mode=2)
        completed = sim.run(max_duration=30.0)
        self.assertTrue(completed, "Stage 2 cruise (30m) and pitch-up yunuslama should reach surface.")
        self.assertLessEqual(sim.dynamics.z, 0.2)
        self.assertGreaterEqual(sim.dynamics.x, 30.0)

if __name__ == '__main__':
    unittest.main()
