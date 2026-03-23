# Specification: Semi-Auto Grid Marking with Iterative Refinement

## Goal
Implement a semi-automatic grid marking feature in the MyPTV `gui_initial_cal.py` for both `extendedZolof` and `TsaiModel`. This feature will allow users to mark a few control points (e.g., 4 corners) and have the system automatically project, snap, and refine the remaining grid points (189+ points) iteratively.

## User Workflow
1. **Target Selection**: User selects a set of points from the target file.
2. **Control Point Marking**: User marks at least 4 control points (corners) in the image.
3. **Iterative Refinement**:
    - User clicks **"Refresh Projection"**.
    - System calculates a Homography/Bilinear mapping based on the control points.
    - System projects all intermediate target points into the image.
    - System "snaps" projected points to the nearest `CalBlobs` (within a radius).
    - Visual feedback shows **Blue** (control), **Green** (snapped), and **Yellow** (projected/unmatched) circles.
    - User can click any yellow circle to add it as a new control point and click "Refresh" again to improve the fit.
4. **Batch Acceptance**: User clicks **"Accept Grid"** to save all Green points to the calibration file and remove them from the active list.

## Functional Requirements

### 1. Automatic Blob Loading
- On GUI startup, check if `cam*_CalBlobs` exists in the calibration folder.
- If found, automatically load and display these blobs so they are available for "snapping" without manual segmentation.

### 2. Grid Projection Engine
- Implement a mapping algorithm (Homography or least-squares fit) that transforms Lab Space $(X, Y, Z)$ to Image Space $(\eta, \zeta)$.
- Use all available manual markers (Control points) to calculate this mapping.
- As more points are marked, the projection accuracy should increase.

### 3. Visual Feedback Layer
- **Control Points (Blue)**: Manually clicked by the user. Used as anchors for the projection.
- **Snapped Points (Green)**: Automatically paired with a blob. These are high-confidence points.
- **Unmatched Points (Yellow)**: Projected but no nearby blob found. Indicates where refinement is needed.

### 4. Interactive Refinement
- Clicking a projected point (Yellow) should allow the user to manually correct it, converting it into a Control point.
- The "Refresh" operation updates the entire grid overlay.

### 5. UI Additions
- **"Mark Grid" Button**: Toggles the grid marking mode.
- **"Refresh" Button**: Re-calculates and re-draws the projected grid.
- **"Accept Grid" Button**: Commits all Green points.

## Technical Implementation Details

### Files to Modify
- `MyPTV/myptv/extendedZolof/gui_initial_cal.py`
- `MyPTV/myptv/TsaiModel/gui_initial_cal.py`
- `MyPTV/myptv/utils.py` (Add projection/homography utilities if needed)

### Changes to `initial_cal_gui` Class
- New attribute `self.control_points`: dictionary mapping `target_index` to image `(x, y)`.
- New attribute `self.projected_points`: dictionary mapping `target_index` to projected `(x, y)` and status (snapped/unmatched).
- Modify `__init__` to load `CalBlobs` automatically.
- New method `calculate_projection()`: uses `scipy.optimize` or `cv2` (if available) to fit the mapping.
- New method `draw_grid_overlay()`: renders circles on the canvas.
- Update `markPoint` logic to handle grid-mode interaction.

## Success Criteria
- User can map a full 189-point grid with significantly fewer than 189 clicks (ideally 4-10 clicks).
- Grid alignment is visually verifiable before saving.
- `CalBlobs` are loaded without user intervention if the file exists.
