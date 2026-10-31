import unittest
import math

class PythonControlAllocator:
    """Python verification model corresponding to firmware/include/navigation/control_allocation.hpp"""
    def __init__(self, is_x_rudder=True, max_angle=25.0):
        self.is_x_rudder = is_x_rudder
        self.max_angle = max_angle
        self.active_fins = [True, True, True, True]

    def allocate(self, tau_pitch, tau_yaw, tau_roll):
        # Clamping
        tau_pitch = max(-1.0, min(1.0, tau_pitch))
        tau_yaw = max(-1.0, min(1.0, tau_yaw))
        tau_roll = max(-1.0, min(1.0, tau_roll))

        p = tau_pitch * self.max_angle
        y = tau_yaw * self.max_angle
        r = tau_roll * self.max_angle

        if not self.is_x_rudder:
            # Cruciform
            delta = [y, y, p + r, p - r]
        else:
            # X-Rudder
            inv_sqrt2 = 1.0 / math.sqrt(2.0)
            delta = [
                inv_sqrt2 * ( p - y + r),
                inv_sqrt2 * ( p + y - r),
                inv_sqrt2 * (-p - y - r),
                inv_sqrt2 * (-p + y + r)
            ]

        for i in range(4):
            if not self.active_fins[i]:
                delta[i] = 0.0
            delta[i] = max(-self.max_angle, min(self.max_angle, delta[i]))

        return delta

    def to_pwm(self, angles):
        pwms = []
        for a in angles:
            norm = max(-1.0, min(1.0, a / self.max_angle))
            pwms.append(int(round(1500 + norm * 500)))
        return pwms

class TestControlAllocation(unittest.TestCase):
    def test_neutral_command(self):
        alloc = PythonControlAllocator(is_x_rudder=True)
        angles = alloc.allocate(0.0, 0.0, 0.0)
        self.assertEqual(angles, [0.0, 0.0, 0.0, 0.0])
        pwms = alloc.to_pwm(angles)
        self.assertEqual(pwms, [1500, 1500, 1500, 1500])

    def test_pure_pitch_up_x_rudder(self):
        alloc = PythonControlAllocator(is_x_rudder=True, max_angle=25.0)
        angles = alloc.allocate(tau_pitch=1.0, tau_yaw=0.0, tau_roll=0.0)
        # All 4 fins should deflect symmetrically to pitch up
        expected_mag = 25.0 / math.sqrt(2.0)
        self.assertAlmostEqual(angles[0], expected_mag, places=2)
        self.assertAlmostEqual(angles[1], expected_mag, places=2)
        self.assertAlmostEqual(angles[2], -expected_mag, places=2)
        self.assertAlmostEqual(angles[3], -expected_mag, places=2)

    def test_pure_yaw_turn_x_rudder(self):
        alloc = PythonControlAllocator(is_x_rudder=True, max_angle=25.0)
        angles = alloc.allocate(tau_pitch=0.0, tau_yaw=1.0, tau_roll=0.0)
        expected_mag = 25.0 / math.sqrt(2.0)
        self.assertAlmostEqual(angles[0], -expected_mag, places=2)
        self.assertAlmostEqual(angles[1], expected_mag, places=2)
        self.assertAlmostEqual(angles[2], -expected_mag, places=2)
        self.assertAlmostEqual(angles[3], expected_mag, places=2)

    def test_fault_tolerance_disabled_fin(self):
        alloc = PythonControlAllocator(is_x_rudder=True)
        alloc.active_fins[1] = False # Fin 2 jammed
        angles = alloc.allocate(tau_pitch=1.0, tau_yaw=0.0, tau_roll=0.0)
        self.assertEqual(angles[1], 0.0)
        self.assertNotEqual(angles[0], 0.0)

if __name__ == '__main__':
    unittest.main()
