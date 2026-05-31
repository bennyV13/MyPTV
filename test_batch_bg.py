
import os
import shutil
import numpy as np
from unittest.mock import MagicMock, patch

# Mock skimage.io and tqdm before importing myptv modules
import sys
mock_io = MagicMock()
mock_rawpy = MagicMock()
mock_tqdm = MagicMock()

sys.modules['skimage'] = MagicMock()
sys.modules['skimage'].io = mock_io
sys.modules['skimage.io'] = mock_io
sys.modules['tqdm'] = mock_tqdm
sys.modules['rawpy'] = mock_rawpy

# Now import the function to test
from myptv.segmentation_mod import calculate_BG_image_batch

def test_batch_bg():
    # Setup dummy directory structure
    test_root = 'test_recordings'
    output_root = 'test_output'
    
    if os.path.exists(test_root): shutil.rmtree(test_root)
    if os.path.exists(output_root): shutil.rmtree(output_root)
    
    os.makedirs(os.path.join(test_root, 'rec1', 'cam1'))
    os.makedirs(os.path.join(test_root, 'rec1', 'cam2'))
    os.makedirs(os.path.join(test_root, 'rec2', 'cam1'))
    os.makedirs(os.path.join(test_root, 'not_a_rec'))
    
    # Create dummy image files
    for d in ['rec1/cam1', 'rec1/cam2', 'rec2/cam1']:
        for i in range(5):
            with open(os.path.join(test_root, d, f'img_{i}.tif'), 'w') as f:
                f.write('dummy')

    # Mock io.imread to return a dummy numpy array with a real dtype
    dummy_img = np.zeros((10, 10), dtype='uint8')
    mock_io.imread.return_value = dummy_img
    
    # Run the batch function
    calculate_BG_image_batch(test_root, output_root, '.tif', N_img=10)
    
    # Check if output files exist
    expected_files = [
        os.path.join(output_root, 'rec1', 'cam1_BG.tif'),
        os.path.join(output_root, 'rec1', 'cam2_BG.tif'),
        os.path.join(output_root, 'rec2', 'cam1_BG.tif'),
    ]
    
    for f in expected_files:
        if os.path.exists(f):
            print(f'PASS: Found {f}')
        else:
            print(f'FAIL: Did not find {f}')
            
    if os.path.exists(os.path.join(output_root, 'not_a_rec')):
        print('FAIL: Found output for not_a_rec')
    else:
        print('PASS: No output for not_a_rec')

    # Cleanup
    shutil.rmtree(test_root)
    shutil.rmtree(output_root)

if __name__ == '__main__':
    test_batch_bg()
