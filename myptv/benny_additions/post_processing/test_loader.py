import numpy as np
import os
from .spatial_coverage import load_data

def test_load_data():
    test_file = "test_data.txt"
    # Create a dummy file with 11 columns, space-separated
    dummy_data = [
        [1, 10.5, 20.5, 30.5, 4, 5, 6, 7, 8, 9, 10],
        [2, 11.5, 21.5, 31.5, 14, 15, 16, 17, 18, 19, 20],
        [3, 12.5, 22.5, 32.5, 24, 25, 26, 27, 28, 29, 30]
    ]
    
    with open(test_file, "w") as f:
        for row in dummy_data:
            f.write(" ".join(map(str, row)) + "\n")
            
    try:
        # Test 3D (default cols 1, 2, 3)
        print(f"Testing 3D load from {test_file}...")
        loaded_3d = load_data(test_file, cols=(1, 2, 3))
        expected_3d = np.array([
            [10.5, 20.5, 30.5],
            [11.5, 21.5, 31.5],
            [12.5, 22.5, 32.5]
        ])
        assert loaded_3d.shape == (3, 3)
        np.testing.assert_array_almost_equal(loaded_3d, expected_3d)
        
        # Test 2D (cols 0, 1)
        print(f"Testing 2D load from {test_file}...")
        loaded_2d = load_data(test_file, cols=(0, 1))
        expected_2d = np.array([
            [1.0, 10.5],
            [2.0, 11.5],
            [3.0, 12.5]
        ])
        assert loaded_2d.shape == (3, 2)
        np.testing.assert_array_almost_equal(loaded_2d, expected_2d)
        
        print("Test passed! Values and shapes are correct.")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_load_data()
