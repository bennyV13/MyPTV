import numpy as np
from .spatial_coverage import generate_grid, calculate_gio

def test_single_particle_3d():
    print("\n--- Testing 3D Single Particle ---")
    ranges = [(0, 100), (0, 100), (-50, 0)]
    resolution = 1.0
    
    grid_points, grid_shape, coords = generate_grid(ranges, resolution)
    assert grid_points.shape[0] == 101 * 101 * 51
    
    particle_pos = np.array([[50.0, 50.0, -25.0]])
    sigma = 3.0
    occupancy = calculate_gio(particle_pos, grid_points, sigma=sigma)
    
    # Check peak
    target_idx = np.where((grid_points == [50.0, 50.0, -25.0]).all(axis=1))[0][0]
    assert np.isclose(occupancy[target_idx], 1.0)
    print("3D Peak Check Passed.")

def test_single_particle_2d():
    print("\n--- Testing 2D Single Particle ---")
    ranges = [(0, 10), (0, 10)]
    resolution = 1.0
    
    grid_points, grid_shape, coords = generate_grid(ranges, resolution)
    assert grid_points.shape[0] == 11 * 11
    
    particle_pos = np.array([[5.0, 5.0]])
    sigma = 2.0
    occupancy = calculate_gio(particle_pos, grid_points, sigma=sigma)
    
    # Peak at (5,5) should be 1.0
    target_idx = np.where((grid_points == [5.0, 5.0]).all(axis=1))[0][0]
    assert np.isclose(occupancy[target_idx], 1.0)
    
    # Score at (5,7) should be exp(-(2^2)/(2*2^2)) = exp(-0.5) = 0.6065
    neighbor_idx = np.where((grid_points == [5.0, 7.0]).all(axis=1))[0][0]
    assert np.isclose(occupancy[neighbor_idx], np.exp(-0.5))
    print("2D Values Check Passed.")

if __name__ == "__main__":
    test_single_particle_3d()
    test_single_particle_2d()
    print("\nAll computation tests passed!")
