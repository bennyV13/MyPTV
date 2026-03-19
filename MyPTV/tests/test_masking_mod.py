import numpy as np
import os
from myptv.masking_mod import load_blobs, get_padded_hull

def test_load_blobs():
    fname = 'test_blobs.txt'
    data = np.array([[10.5, 20.5, 0, 0, 0, 0], [30.5, 40.5, 0, 0, 0, 0]])
    np.savetxt(fname, data, delimiter='\t')
    try:
        blobs = load_blobs(fname)
        assert np.allclose(blobs, [[10.5, 20.5], [30.5, 40.5]])
    finally:
        if os.path.exists(fname): os.remove(fname)

def test_get_padded_hull():
    # Square CW in image coordinates
    points = np.array([[10, 10], [20, 10], [20, 20], [10, 20]])
    padding = 5
    padded = get_padded_hull(points, padding)
    assert len(padded) == 4
    
    # Expected: [[10-5, 10-5], [20+5, 10-5], [20+5, 20+5], [10-5, 20+5]]
    # (roughly, bisector math is exact for squares)
    expected = np.array([[5, 5], [25, 5], [25, 25], [5, 25]])
    # We sort both to compare because ConvexHull might start at different vertex
    assert np.allclose(np.sort(padded, axis=0), np.sort(expected, axis=0), atol=1e-1)
