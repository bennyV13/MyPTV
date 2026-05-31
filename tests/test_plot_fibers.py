import pytest
import numpy as np
from myptv.makePlots.plot_trajectories import plot_fibers

def test_plot_fibers_missing_files():
    with pytest.raises(FileNotFoundError):
        plot_fibers("non_existent_traj.txt", "non_existent_ori.txt", min_length=5)


def test_plot_fibers_execution(tmp_path):
    # Create mock trajectory file (ID, x, y, z, vx, vy, vz, ax, ay, az, frame)
    traj_file = tmp_path / "mock_traj.txt"
    traj_data = np.array([
        [1, 10.0, 20.0, 30.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [1, 11.0, 20.0, 30.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [1, 12.0, 20.0, 30.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0]
    ])
    np.savetxt(traj_file, traj_data, delimiter='\t', fmt='%.3f')

    # Create mock orientations file (ID, px, py, pz, c1, c2, c3, c4, err, frame)
    ori_file = tmp_path / "mock_ori.txt"
    ori_data = np.array([
        [1, 1.0, 0.0, 0.0, 0, 0, 0, 0, 0.0, 0.0],
        [1, 0.0, 1.0, 0.0, 0, 0, 0, 0, 0.0, 1.0],
        [1, 0.0, 0.0, 1.0, 0, 0, 0, 0, 0.0, 2.0]
    ])
    np.savetxt(ori_file, ori_data, delimiter='\t', fmt='%.3f')

    # Mock plt.show
    import matplotlib.pyplot as plt
    original_show = plt.show
    plt.show = lambda: None

    try:
        # Test both modes
        plot_fibers(str(traj_file), str(ori_file), min_length=2, mode='centered_rod')
        plot_fibers(str(traj_file), str(ori_file), min_length=2, mode='path_and_half_rod')
    finally:
        plt.show = original_show

