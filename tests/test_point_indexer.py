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
