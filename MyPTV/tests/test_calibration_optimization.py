import unittest
import numpy as np
from myptv.extendedZolof.optimize_calibration import PointManager, OptimizerCore
from unittest.mock import MagicMock

class TestPointManager(unittest.TestCase):
    # ... existing test ...
    def test_group_by_xz(self):
        # ... existing ...
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

class TestOptimizerCore(unittest.TestCase):
    def setUp(self):
        self.data = np.array([
            [1.0, 1.0, 10.0, 100.0, 5.0],
            [1.1, 1.1, 10.0, 200.0, 5.0],
            [2.0, 2.0, 20.0, 100.0, 5.0],
            [2.1, 2.1, 20.0, 200.0, 5.0],
            [2.2, 2.2, 20.0, 300.0, 5.0],
        ])
        self.pm = PointManager(self.data)
        self.optimizer = OptimizerCore("cam1", self.pm, k=1)

    def test_get_mse_interaction(self):
        # We'll mock the external dependencies to see if they are called.
        with unittest.mock.patch('myptv.extendedZolof.optimize_calibration.camera_extendedZolof') as mock_cam_cls, \
             unittest.mock.patch('myptv.extendedZolof.optimize_calibration.calibrate_extendedZolof') as mock_cal_cls:
            
            mock_cal_inst = mock_cal_cls.return_value
            mock_cal_inst.mean_squared_err.return_value = 0.42
            
            pm = PointManager(self.data)
            optimizer = OptimizerCore("cam1", pm, k=1)
            
            mse = optimizer.get_mse(self.data[:2])
            
            self.assertEqual(mse, 0.42)
            mock_cam_cls.assert_called_with("cam1")
            mock_cal_cls.assert_called()
            mock_cal_inst.calibrate.assert_called()

    def test_optimize_local(self):
        # We'll mock get_mse to return values that favor a certain selection.
        # Suppose we have 2 groups, and we want to pick 1 point from each.
        # Group 1 has 2 points, Group 2 has 3 points.
        
        with unittest.mock.patch.object(OptimizerCore, 'get_mse') as mock_mse:
            # Let's say MSE is the sum of selected indices (very simple model)
            # So (index 0 from G1, index 0 from G2) gives MSE 0 (the best).
            mock_mse.side_effect = lambda points: np.sum(points[:, 0]) 
            
            # Re-initialize to ensure everything is clean
            pm = PointManager(self.data)
            optimizer = OptimizerCore("cam1", pm, k=1)
            
            # Since the data in my test has x_cam as first column:
            # [1.0, 1.1] for G1
            # [2.0, 2.1, 2.2] for G2
            # Sum will be minimized if we pick 1.0 from G1 and 2.0 from G2.
            
            best_mse, best_points = optimizer.optimize_local()
            
            self.assertEqual(best_mse, 3.0) # 1.0 + 2.0
            self.assertEqual(len(best_points), 2)
            self.assertIn(1.0, best_points[:, 0])
            self.assertIn(2.0, best_points[:, 0])

    def test_run_multi_start(self):
        # We'll mock optimize_local to return different values on each call.
        with unittest.mock.patch.object(OptimizerCore, 'optimize_local') as mock_opt:
            mock_opt.side_effect = [
                (0.5, np.array([[1.1]])),
                (0.3, np.array([[1.0]])),
                (0.4, np.array([[1.2]]))
            ]
            
            pm = PointManager(self.data)
            optimizer = OptimizerCore("cam1", pm, k=1)
            
            best_mse, best_points = optimizer.run_multi_start(n_starts=3)
            
            self.assertEqual(best_mse, 0.3)
            np.testing.assert_array_equal(best_points, np.array([[1.0]]))
            self.assertEqual(mock_opt.call_count, 3)

if __name__ == '__main__':
    unittest.main()
