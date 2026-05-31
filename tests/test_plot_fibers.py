import pytest
from myptv.makePlots.plot_trajectories import plot_fibers

def test_plot_fibers_missing_files():
    with pytest.raises(FileNotFoundError):
        plot_fibers("non_existent_traj.txt", "non_existent_ori.txt", min_length=5)
