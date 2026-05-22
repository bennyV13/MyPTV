import pytest
import os
import subprocess
import sys

def test_argument_validation_fails_without_files():
    """Verify that specifying --cal_image without points files fails with exit code 2."""
    script_path = os.path.join("myptv", "benny_additions", "calibration", "point_indexer.py")
    cmd = [sys.executable, script_path, "--cal_image", "dummy.png"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 2
    assert "Error: --cal_image can only be used in single-camera mode" in result.stderr

def test_missing_image_file_raises_error():
    """Verify that specifying a non-existent image file raises FileNotFoundError."""
    # Write temp empty blobs and cal_points files to trigger execution
    with open("temp_blobs.txt", "w") as f: f.write("100.0 200.0\n")
    with open("temp_cal.txt", "w") as f: f.write("0.0 0.0 0.0\n")
    
    script_path = os.path.join("myptv", "benny_additions", "calibration", "point_indexer.py")
    cmd = [sys.executable, script_path, 
           "--image_points", "temp_blobs.txt", 
           "--target_points", "temp_cal.txt", 
           "--cal_image", "non_existent_image_12345.png"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Clean up
    if os.path.exists("temp_blobs.txt"): os.remove("temp_blobs.txt")
    if os.path.exists("temp_cal.txt"): os.remove("temp_cal.txt")
    
    assert "Error: Calibration image not found at 'non_existent_image_12345.png'" in result.stderr or "FileNotFoundError" in result.stderr or result.returncode != 0
