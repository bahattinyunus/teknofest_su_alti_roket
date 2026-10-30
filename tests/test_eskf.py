import unittest
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class SimpleESKFModel:
    """Python reference model corresponding to firmware/include/navigation/eskf.hpp"""
    def __init__(self):
        self.depth = 0.0
        self.vz = 0.0
        self.pitch = 0.0
        self.p = np.eye(3) * 0.1
        self.q = np.eye(3) * 0.01
        self.r = np.eye(2) * 0.05

    def predict(self, accel_z, gyro_pitch, dt):
        self.depth += self.vz * dt + 0.5 * accel_z * (dt ** 2)
        self.vz += accel_z * dt
        self.pitch += gyro_pitch * dt

        f = np.eye(3)
        f[0, 1] = dt
        self.p = f @ self.p @ f.T + self.q

    def update(self, meas_depth, meas_pitch):
        h = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
        z = np.array([meas_depth, meas_pitch])
        y = z - h @ np.array([self.depth, self.vz, self.pitch])
        s = h @ self.p @ h.T + self.r
        k = self.p @ h.T @ np.linalg.inv(s)

        state = np.array([self.depth, self.vz, self.pitch]) + k @ y
        self.depth, self.vz, self.pitch = state[0], state[1], state[2]
        self.p = (np.eye(3) - k @ h) @ self.p

class TestESKF(unittest.TestCase):
    def test_depth_convergence_with_noisy_measurements(self):
        eskf = SimpleESKFModel()
        true_depth = 1.8
        dt = 0.02

        # Run 100 iterations of noisy measurements around 1.8m
        np.random.seed(42)
        for _ in range(100):
            noise = np.random.normal(0, 0.08)
            measured_depth = true_depth + noise
            measured_pitch = 0.0 + np.random.normal(0, 0.5)

            eskf.predict(accel_z=0.0, gyro_pitch=0.0, dt=dt)
            eskf.update(measured_depth, measured_pitch)

        self.assertAlmostEqual(eskf.depth, true_depth, delta=0.05)

if __name__ == '__main__':
    unittest.main()
