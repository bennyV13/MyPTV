import numpy as np
import os
from PIL import Image
from .spatial_coverage import load_mask, generate_grid, calculate_gio

def test_orientation_and_resolution():
    print("Test 1: Orientation and Resolution Mapping...")
    mask_path = "test_adv_mask.tif"
    # 20x20 mask, all invalid except (x=15, y=5)
    mask_data = np.zeros((20, 20), dtype=np.uint8)
    mask_data[5, 15] = 255 # Row 5, Col 15 -> Y=5, X=15
    Image.fromarray(mask_data).save(mask_path)
    
    try:
        loaded_mask = load_mask(mask_path)
        
        # Test with high resolution (0.5)
        res = 0.5
        ranges = [(0, 19), (0, 19)]
        grid_points, grid_shape, coords = generate_grid(ranges, res)
        
        mask_h, mask_w = loaded_mask.shape
        gx = np.clip(grid_points[:, 0].astype(int), 0, mask_w - 1)
        gy = np.clip(grid_points[:, 1].astype(int), 0, mask_h - 1)
        valid_mask = loaded_mask[gy, gx]
        
        # Point (15.0, 5.0) should be valid
        # Also (15.1, 5.1), (15.4, 5.4) because they cast to int 15, 5
        idx_15_5 = np.where((grid_points == [15.0, 5.0]).all(axis=1))[0][0]
        assert valid_mask[idx_15_5] == True
        
        idx_15_5_offset = np.where((grid_points == [15.5, 5.5]).all(axis=1))[0][0]
        assert valid_mask[idx_15_5_offset] == True
        
        # Point (5.0, 15.0) should be invalid (confirms it's not flipped)
        idx_5_15 = np.where((grid_points == [5.0, 15.0]).all(axis=1))[0][0]
        assert valid_mask[idx_5_15] == False
        
        print("  - Orientation/Resolution: PASSED")

    finally:
        if os.path.exists(mask_path): os.remove(mask_path)

def test_clipping():
    print("Test 2: Boundary Clipping...")
    mask_path = "test_clip_mask.tif"
    # 10x10 mask, all valid
    mask_data = np.ones((10, 10), dtype=np.uint8) * 255
    Image.fromarray(mask_data).save(mask_path)
    
    try:
        loaded_mask = load_mask(mask_path)
        # Grid range extends beyond mask: -5 to 15
        ranges = [(-5, 15), (-5, 15)]
        grid_points, grid_shape, coords = generate_grid(ranges, 1.0)
        
        mask_h, mask_w = loaded_mask.shape
        gx = np.clip(grid_points[:, 0].astype(int), 0, mask_w - 1)
        gy = np.clip(grid_points[:, 1].astype(int), 0, mask_h - 1)
        valid_mask = loaded_mask[gy, gx]
        
        # All points should be valid because they clip to the "all valid" 10x10 area
        assert np.all(valid_mask == True)
        print("  - Boundary Clipping: PASSED")
        
    finally:
        if os.path.exists(mask_path): os.remove(mask_path)

def test_coverage_stat_integration():
    print("Test 3: End-to-End Coverage Simulation...")
    mask_path = "test_sim_mask.tif"
    # 20x20 mask, a 10x10 square in the middle is valid
    # Middle is x:5-14, y:5-14 (Area = 100 pixels)
    mask_data = np.zeros((20, 20), dtype=np.uint8)
    mask_data[5:15, 5:15] = 255
    Image.fromarray(mask_data).save(mask_path)
    
    try:
        loaded_mask = load_mask(mask_path)
        ranges = [(0, 19), (0, 19)]
        grid_points, grid_shape, coords = generate_grid(ranges, 1.0)
        
        mask_h, mask_w = loaded_mask.shape
        gx = np.clip(grid_points[:, 0].astype(int), 0, mask_w - 1)
        gy = np.clip(grid_points[:, 1].astype(int), 0, mask_h - 1)
        valid_mask = loaded_mask[gy, gx]
        
        total_valid = np.sum(valid_mask)
        assert total_valid == 100, f"Expected 100 valid points, got {total_valid}"
        
        # Place one particle in the middle of the valid zone (10, 10)
        particles = np.array([[10.0, 10.0]])
        occupancy = calculate_gio(particles, grid_points, sigma=2.0)
        
        # Coverage only within mask
        occupied_valid = np.sum((occupancy > 0.01) & valid_mask)
        coverage_pct = (occupied_valid / total_valid) * 100
        
        # Sigma 2.0 -> Cutoff 6.0
        # All grid points within dist 6.0 of (10,10) are covered.
        # Since the valid box is (5-14, 5-14), and particle is at (10,10),
        # most of the circle fits inside the valid box.
        print(f"  - Calculated Coverage in valid zone: {coverage_pct:.2f}%")
        assert coverage_pct > 0, "Coverage should be non-zero"
        
        # Verify that an occupied point OUTSIDE the mask doesn't count
        # Place particle at (1, 1) - outside the (5-14) box
        particles_2 = np.array([[1.0, 1.0]])
        occupancy_2 = calculate_gio(particles_2, grid_points, sigma=1.0) # small sigma
        
        occupied_valid_2 = np.sum((occupancy_2 > 0.01) & valid_mask)
        assert occupied_valid_2 == 0, "Points outside mask should not contribute to coverage"
        
        print("  - Integration Stats: PASSED")

    finally:
        if os.path.exists(mask_path): os.remove(mask_path)

if __name__ == "__main__":
    try:
        test_orientation_and_resolution()
        test_clipping()
        test_coverage_stat_integration()
        print("\nAdvanced masking tests completed successfully!")
    except Exception as e:
        print(f"\nAdvanced test FAILED: {e}")
        import traceback
        traceback.print_exc()
