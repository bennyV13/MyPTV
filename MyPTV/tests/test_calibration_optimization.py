import unittest
import numpy as np
from myptv.extendedZolof.optimize_calibration import PointManager

class TestPointManager(unittest.TestCase):
    def test_group_by_xz(self):
        # Create synthetic data: x_cam, y_cam, X_lab, Y_lab, Z_lab
        # Column 1: (X=10, Z=5)
        # Column 2: (X=20, Z=5)
        data = np.array([
            [1.0, 1.0, 10.0, 100.0, 5.0],
            [1.1, 1.1, 10.0, 200.0, 5.0],
            [2.0, 2.0, 20.0, 100.0, 5.0],
            [2.1, 2.1, 20.0, 200.0, 5.0],
            [2.2, 2.2, 20.0, 300.0, 5.0],
        ])
        
        pm = PointManager(data)
        groups = pm.get_groups()
        
        # We expect 2 groups (columns)
        self.assertEqual(len(groups), 2)
        
        # Check column 1 (X=10, Z=5)
        key1 = (10.0, 5.0)
        self.assertIn(key1, groups)
        self.assertEqual(len(groups[key1]), 2)
        
        # Check column 2 (X=20, Z=5)
        key2 = (20.0, 5.0)
        self.assertIn(key2, groups)
        self.assertEqual(len(groups[key2]), 3)

if __name__ == '__main__':
    unittest.main()
