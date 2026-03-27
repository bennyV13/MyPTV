import unittest
import numpy as np
from scripts.lagrangian_analysis import LagrangianAnalysis

class TestLagrangianStats(unittest.TestCase):
    
    def setUp(self):
        # Create a simple synthetic trajectory: linear motion
        # id, x, y, z, vx, vy, vz, ax, ay, az, frame
        # pos = t, vel = 1, acc = 0
        self.dt = 1.0
        t = np.arange(10)
        traj = np.zeros((10, 11))
        traj[:, 0] = 1 # id
        traj[:, 1] = t # x
        traj[:, 2] = t # y
        traj[:, 3] = t # z
        traj[:, 4] = 1 # vx
        traj[:, 5] = 1 # vy
        traj[:, 6] = 1 # vz
        traj[:, 10] = t # frame
        
        self.analysis = LagrangianAnalysis(traj_list=[traj])

    def test_msd_linear(self):
        # For x=t, y=t, z=t, MSD = (lag^2 + lag^2 + lag^2) = 3 * lag^2
        max_lag = 5
        msd = self.analysis.calculate_msd(max_lag=max_lag)
        lags = np.arange(max_lag)
        expected_msd = 3 * lags**2
        np.testing.assert_array_almost_equal(msd, expected_msd)

    def test_lvacf_linear(self):
        # For constant velocity, LVACF should be 1.0 for all lags
        max_lag = 5
        lvacf = self.analysis.calculate_lvacf(kind='vx', max_lag=max_lag)
        # However, since v_std is 0 for constant velocity, we expect 0 or NaN 
        # based on implementation. Our implementation uses v_std from ALL trajs.
        # If we have only one constant-v traj, v_std is 0.
        # Let's add a second traj with different velocity to get non-zero std.
        t = np.arange(10)
        traj2 = np.zeros((10, 11))
        traj2[:, 0] = 2
        traj2[:, 4] = 2 # Different vx
        traj2[:, 10] = t
        
        analysis2 = LagrangianAnalysis(traj_list=[self.analysis.trajs[0], traj2])
        lvacf = analysis2.calculate_lvacf(kind='vx', max_lag=max_lag)
        
        # For constant velocities in each trajectory, 
        # v_prime = v - v_mean is also constant.
        # Correlation should be 1.0
        np.testing.assert_array_almost_equal(lvacf, np.ones(max_lag))

    def test_structure_function_linear(self):
        # For x=t, vx=1. dv = 1 - 1 = 0.
        max_lag = 5
        sf2 = self.analysis.calculate_structure_function(kind='vx', order=2, max_lag=max_lag)
        np.testing.assert_array_almost_equal(sf2[1:], np.zeros(max_lag-1))

if __name__ == "__main__":
    unittest.main()
