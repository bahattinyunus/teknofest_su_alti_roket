import unittest
import struct
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from gcs.blackbox_parser import BlackboxParser, RECORD_FORMAT

class TestBlackboxParser(unittest.TestCase):
    def setUp(self):
        self.parser = BlackboxParser()

    def test_parse_binary_single_record(self):
        # Format: ts(I), depth(f), pitch(f), heading(f), motor(f), fin_offset(B), state(B)
        raw = struct.pack(RECORD_FORMAT, 1000, 1.5, 5.2, 180.0, 1750.0, 50, 2)
        records = self.parser.parse_binary(raw)

        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertEqual(r["timestamp_ms"], 1000)
        self.assertAlmostEqual(r["depth_m"], 1.5, places=2)
        self.assertAlmostEqual(r["pitch_deg"], 5.2, places=1)
        self.assertAlmostEqual(r["heading_deg"], 180.0, places=1)
        self.assertEqual(r["fin_top_pwm"], 1550)
        self.assertEqual(r["mission_state"], 2)

    def test_compute_summary(self):
        raw = bytearray()
        raw.extend(struct.pack(RECORD_FORMAT, 0, 0.5, 0.0, 0.0, 1500.0, 0, 1))
        raw.extend(struct.pack(RECORD_FORMAT, 1000, 1.8, 15.0, 90.0, 1750.0, 20, 2))
        raw.extend(struct.pack(RECORD_FORMAT, 2000, 1.2, -5.0, 180.0, 1750.0, 10, 3))

        self.parser.parse_binary(bytes(raw))
        summary = self.parser.compute_summary()

        self.assertEqual(summary["total_records"], 3)
        self.assertEqual(summary["mission_duration_s"], 2.0)
        self.assertAlmostEqual(summary["max_depth_m"], 1.8, places=2)
        self.assertAlmostEqual(summary["max_pitch_deg"], 15.0, places=1)

if __name__ == '__main__':
    unittest.main()
