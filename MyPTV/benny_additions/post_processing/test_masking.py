import numpy as np
import os
from PIL import Image
from .spatial_coverage import load_mask, generate_grid

def test_masking_logic():
    print("\n--- Testing Masking Logic ---")
    
    # 1. Create a dummy TIFF mask (10x10)
    # Left half (0-4) is invalid (0), Right half (5-9) is valid (255)
    mask_data = np.zeros((10, 10), dtype=np.uint8)
    mask_data[:, 5:] = 255
    mask_path = "test_mask.tif"
    Image.fromarray(mask_data).save(mask_path)
    
    try:
        # 2. Load mask
        loaded_mask = load_mask(mask_path)
        assert loaded_mask.shape == (10, 10)
        assert np.all(loaded_mask[:, :5] == False)
        assert np.all(loaded_mask[:, 5:] == True)
        print("Mask loading passed.")
        
        # 3. Generate a grid and apply masking logic manually as done in main()
        # Range 0-9, Resolution 1.0 -> points at 0, 1, ..., 9
        ranges = [(0, 9), (0, 9)]
        grid_points, grid_shape, grid_coords = generate_grid(ranges, resolution=1.0)
        
        # Manual implementation of the clipping and indexing logic from main()
        mask_h, mask_w = loaded_mask.shape
        gx = np.clip(grid_points[:, 0].astype(int), 0, mask_w - 1)
        gy = np.clip(grid_points[:, 1].astype(int), 0, mask_h - 1)
        valid_mask = loaded_mask[gy, gx]
        
        # Check specific points
        # Point (2, 2) -> Left half -> Invalid
        idx_2_2 = np.where((grid_points == [2.0, 2.0]).all(axis=1))[0][0]
        assert valid_mask[idx_2_2] == False, f"Point (2,2) should be invalid"
        
        # Point (7, 5) -> Right half -> Valid
        idx_7_5 = np.where((grid_points == [7.0, 5.0]).all(axis=1))[0][0]
        assert valid_mask[idx_7_5] == True, f"Point (7,5) should be valid"
        
        print(f"Grid filtering passed. {np.sum(valid_mask)}/{len(valid_mask)} points valid.")
        
        # 4. Test Coordinate Mapping (Orientation)
        # Image convention: [row, col] -> [y, x]
        # Our grid: [x, y]
        # Let's put a single valid pixel at x=8, y=3
        mask_data_2 = np.zeros((10, 10), dtype=np.uint8)
        mask_data_2[3, 8] = 255 # row 3, col 8
        Image.fromarray(mask_data_2).save(mask_path)
        
        loaded_mask_2 = load_mask(mask_path)
        gx2 = np.clip(grid_points[:, 0].astype(int), 0, mask_w - 1)
        gy2 = np.clip(grid_points[:, 1].astype(int), 0, mask_h - 1)
        valid_mask_2 = loaded_mask_2[gy2, gx2]
        
        idx_8_3 = np.where((grid_points == [8.0, 3.0]).all(axis=1))[0][0]
        assert valid_mask_2[idx_8_3] == True, "Coordinate (8,3) should map to mask[3, 8]"
        
        print("Coordinate mapping (X,Y -> Row,Col) passed.")

    finally:
        if os.path.exists(mask_path):
            os.remove(mask_path)

if __name__ == "__main__":
    try:
        test_masking_logic()
        print("\nAll masking tests passed!")
    except AssertionError as e:
        print(f"\nTest FAILED: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
