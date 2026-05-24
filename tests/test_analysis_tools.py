import pytest
import numpy as np
from myptv.data_analysis.analysis_tools import (
    get_trajectory_velocities,
    get_velocity_list,
    get_mean_std_time_series,
    get_mean_velocity_profiles,
    get_std_velocity_profiles
)

# Mock trajectories for testing
# Trajectories shape is usually (N_points, 11)
# Column indices in trajectories:
# 0: traj_id, 1: x, 2: y, 3: z, 4: vx, 5: vy, 6: vz, 7: ax, 8: ay, 9: az, 10: time
mock_traj = np.array([
    [1, 10.0, 20.0, 30.0, 1.0, 2.0, 3.0, 0.1, 0.2, 0.3, 0.0],
    [1, 11.0, 22.0, 33.0, 1.5, 2.5, 3.5, 0.1, 0.2, 0.3, 1.0],
    [1, 12.0, 24.0, 36.0, 2.0, 3.0, 4.0, 0.1, 0.2, 0.3, 2.0]
])
mock_traj_list = [mock_traj]


def test_get_trajectory_velocities_validation():
    # Valid kinds
    assert len(get_trajectory_velocities(mock_traj_list, kind='x')) == 1
    assert len(get_trajectory_velocities(mock_traj_list, kind='y')) == 1
    assert len(get_trajectory_velocities(mock_traj_list, kind='z')) == 1
    assert len(get_trajectory_velocities(mock_traj_list, kind='KE')) == 1
    
    # Invalid kind should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        get_trajectory_velocities(mock_traj_list, kind='')
    assert 'undefined kind ""' in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        get_trajectory_velocities(mock_traj_list, kind='invalid')
    assert 'undefined kind "invalid"' in str(excinfo.value)


def test_get_velocity_list_validation():
    # Valid kinds
    assert len(get_velocity_list(mock_traj_list, kind='x')) == 3
    assert len(get_velocity_list(mock_traj_list, kind='ax')) == 3
    
    # Invalid kind should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        get_velocity_list(mock_traj_list, kind='')
    assert 'undefined kind ""' in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        get_velocity_list(mock_traj_list, kind='invalid')
    assert 'undefined kind "invalid"' in str(excinfo.value)


def test_get_mean_std_time_series_validation():
    # Valid kinds
    assert len(get_mean_std_time_series(mock_traj_list, kind='x')) == 3
    
    # Invalid kind should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        get_mean_std_time_series(mock_traj_list, kind='')
    assert 'undefined kind ""' in str(excinfo.value)


def test_get_mean_velocity_profiles_validation():
    # Valid kinds/directions
    res = get_mean_velocity_profiles(mock_traj_list, start=10.0, stop=40.0, nbins=3, direction='x', kind='x')
    assert res.shape == (2, 3)
    
    # Invalid kind should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        get_mean_velocity_profiles(mock_traj_list, start=10.0, stop=40.0, nbins=3, direction='x', kind='')
    assert 'undefined kind ""' in str(excinfo.value)
    
    # Invalid direction should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        get_mean_velocity_profiles(mock_traj_list, start=10.0, stop=40.0, nbins=3, direction='', kind='x')
    assert 'undefined direction ""' in str(excinfo.value)


def test_get_std_velocity_profiles_validation():
    # Valid kinds/directions
    res = get_std_velocity_profiles(mock_traj_list, start=10.0, stop=40.0, nbins=3, direction='x', kind='x')
    assert res.shape == (2, 3)
    
    # Invalid kind should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        get_std_velocity_profiles(mock_traj_list, start=10.0, stop=40.0, nbins=3, direction='x', kind='')
    assert 'undefined kind ""' in str(excinfo.value)
    
    # Invalid direction should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        get_std_velocity_profiles(mock_traj_list, start=10.0, stop=40.0, nbins=3, direction='', kind='x')
    assert 'undefined direction ""' in str(excinfo.value)
