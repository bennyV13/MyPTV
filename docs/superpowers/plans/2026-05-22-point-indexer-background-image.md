# Calibration Background Image in Point Indexer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow users to display a semi-transparent calibration image in the background of the point indexing validation plot when using `point_indexer.py` in single-camera mode.

**Architecture:** Extend command-line arguments to accept `--cal_image` in single-camera mode. If provided, strictly load the image and display it using `plt.imshow(..., alpha=0.6, cmap='gray')` in `save_and_plot`. Ensure robust input validation and clean error handling.

**Tech Stack:** Python 3, argparse, matplotlib, numpy, pytest

---

### Task 1: Switch to master branch and setup tests
**Files:**
- Test: `tests/test_point_indexer.py`

- [ ] **Step 1: Switch to master branch**
Run: `git checkout master` in `/Users/user/Desktop/Research/myptv_top`
Expected: Switched to branch 'master'

- [ ] **Step 2: Write failing unit test for argument parsing and image validation**
Create a new file `tests/test_point_indexer.py` with the following content:
```python
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
```

- [ ] **Step 3: Run pytest to verify it fails**
Run: `pytest tests/test_point_indexer.py -v` in `/Users/user/Desktop/Research/myptv_top`
Expected: FAIL (or command error since the argument is not yet supported in `point_indexer.py`, so the parser will complain about unrecognized arguments or fail differently)

- [ ] **Step 4: Commit**
```bash
git add tests/test_point_indexer.py
git commit -m "test: add initial failing test for point_indexer argument validation"
```

### Task 2: Implement CLI Argument & Validation logic
**Files:**
- Modify: `myptv/benny_additions/calibration/point_indexer.py`

- [ ] **Step 1: Add `--cal_image` argument and its validation in `point_indexer.py`**
In `/Users/user/Desktop/Research/myptv_top/myptv/benny_additions/calibration/point_indexer.py`:
Add the parser argument:
```python
    parser.add_argument("--cal_image", help="Path to the background calibration image (e.g. image.png)")
```
And add the validation before processing files:
```python
    # Validate arguments
    if args.cal_image:
        if not (args.image_points and args.target_points):
            parser.error("Error: --cal_image can only be used in single-camera mode. "
                         "Please provide both --image_points and --target_points.")
```

- [ ] **Step 2: Run pytest to verify Task 1 tests now pass**
Run: `pytest tests/test_point_indexer.py -v`
Expected: PASS

- [ ] **Step 3: Add further validation tests for non-existent background image**
Append to `tests/test_point_indexer.py`:
```python
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
```

- [ ] **Step 4: Run pytest and verify it fails**
Run: `pytest tests/test_point_indexer.py -v`
Expected: FAIL (missing image doesn't raise error/exit yet because we haven't implemented loading in `save_and_plot`)

- [ ] **Step 5: Commit**
```bash
git add myptv/benny_additions/calibration/point_indexer.py tests/test_point_indexer.py
git commit -m "feat: add CLI argument and validation logic for point_indexer background image"
```

### Task 3: Implement Image Overlay in Plotting Logic
**Files:**
- Modify: `myptv/benny_additions/calibration/point_indexer.py`

- [ ] **Step 1: Implement background image overlay in `save_and_plot` and pass `args.cal_image`**
In `/Users/user/Desktop/Research/myptv_top/myptv/benny_additions/calibration/point_indexer.py`:
Update `save_and_plot` definition and body:
```python
def save_and_plot(indexed_rows, output_csv, output_plot, camera_name, create_plot=True, cal_image_path=None):
    """
    Saves the indexed points to a CSV and optionally generates a validation plot.
    """
    headers = ["CameraID", "ImagePath", "Plane", "PixelX", "PixelY", "WorldX", "WorldY", "WorldZ"]
    df = pd.DataFrame(indexed_rows, columns=headers)
    df.to_csv(output_csv, index=False)
    
    if not create_plot:
        print(f"Successfully processed {camera_name}. (Plot skipped)")
        return

    import matplotlib.pyplot as plt
    
    # Plotting for Human Approval
    plt.figure(figsize=(10, 8))
    
    if cal_image_path:
        if not os.path.exists(cal_image_path):
            raise FileNotFoundError(f"Error: Calibration image not found at '{cal_image_path}'")
        try:
            img = plt.imread(cal_image_path)
            cmap = 'gray' if len(img.shape) == 2 else None
            plt.imshow(img, cmap=cmap, alpha=0.6)
        except Exception as e:
            raise RuntimeError(f"Error: Failed to load calibration image '{cal_image_path}': {e}")
```
And pass `args.cal_image` in the caller inside `__main__`:
```python
        save_and_plot(rows, output_csv, output_plot, f"Cam {args.camera_id}", 
                      create_plot=create_plot, cal_image_path=args.cal_image)
```

- [ ] **Step 2: Run pytest to verify all tests pass**
Run: `pytest tests/test_point_indexer.py -v`
Expected: PASS

- [ ] **Step 3: Commit**
```bash
git add myptv/benny_additions/calibration/point_indexer.py
git commit -m "feat: implement image loading and background overlay in save_and_plot"
```
