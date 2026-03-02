import unittest
import sys
import os

# Add src to path relative to this file's location
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..', 'src'))
sys.path.append(src_dir)

from navigation.kalman import KalmanFilter1D
from navigation.pid_controller import PIDController

class TestNavigation(unittest.TestCase):
    def test_kalman_filter(self):
        kf = KalmanFilter1D(0.01, 0.1, 1.0, 0)
        # Test if it converges towards the measurement (10.0)
        filtered = kf.update(10.0)
        self.assertGreater(filtered, 0)
        self.assertLess(filtered, 10.0)
        
        # Multiple updates should get closer
        for _ in range(10):
            filtered = kf.update(10.0)
        self.assertGreater(filtered, 9.0)

    def test_pid_controller(self):
        pid = PIDController(kp=1.0, ki=0.1, kd=0.05, setpoint=10)
        # With current value 0, error is 10, output should be positive
        output = pid.update(0)
        self.assertGreater(output, 0)
        
        # With current value 20, error is -10, output should be negative
        output = pid.update(20)
        self.assertLess(output, 0)

if __name__ == '__main__':
    unittest.main()
