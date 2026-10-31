import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis', 'structural')))

from pressure_hull_thickness import SubseaHullAnalysis

class TestStructuralAnalysis(unittest.TestCase):
    def test_acrylic_hull_safety_at_10m(self):
        analysis = SubseaHullAnalysis(outer_diameter_mm=150.0, wall_thickness_mm=5.0, material_key="ACRYLIC_PMMA")
        res = analysis.compute_safety_at_depth(depth_m=10.0)

        self.assertAlmostEqual(res["hydrostatic_pressure_bar"], 1.005, places=2)
        self.assertGreater(res["fos_yield"], 10.0) # Yield safety factor is very large at 10m
        self.assertGreater(res["fos_buckling"], 2.5) # Buckling collapse safety factor (> 2.5 is standard safe)
        self.assertEqual(res["structural_status"], "PASSED (SAFE)")

    def test_aluminum_hull_strength(self):
        analysis_al = SubseaHullAnalysis(outer_diameter_mm=150.0, wall_thickness_mm=3.0, material_key="ALUMINUM_6061_T6")
        res = analysis_al.compute_safety_at_depth(depth_m=20.0)

        self.assertGreater(res["fos_yield"], 30.0)
        self.assertGreater(res["critical_buckling_pressure_bar"], 15.0)

if __name__ == '__main__':
    unittest.main()
