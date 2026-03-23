# Semi-Auto Grid Marking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a semi-automatic grid marking feature in `gui_initial_cal.py` allowing 4-corner marking + iterative refinement.

**Architecture:** Add a `GridController` to the GUI that manages control points, computes an image-to-lab mapping using a least-squares affine/homography fit, and provides an overlay for snapping projected points to detected blobs.

**Tech Stack:** Python, Tkinter, NumPy, SciPy.

---

### Task 1: Auto-Loading & Structural Prep

**Files:**
- Modify: `MyPTV/myptv/extendedZolof/gui_initial_cal.py`
- Modify: `MyPTV/myptv/TsaiModel/gui_initial_cal.py`

- [ ] **Step 1: Implement `load_existing_blobs` in `__init__`**
  Check if `cam*_CalBlobs` exists and load it into `self.segmented` if not already there.
- [ ] **Step 2: Add Grid State Variables**
  Initialize `self.grid_mode = False`, `self.control_points = {}` (map target_index -> (x,y)), `self.grid_overlays = []`.
- [ ] **Step 3: Enable Multi-Select in Target Listbox**
  Set `selectmode='extended'` for `self.target_listbox`.
- [ ] **Step 4: Commit**

### Task 2: Projection Engine (`utils.py`)

**Files:**
- Modify: `MyPTV/myptv/utils.py`

- [ ] **Step 1: Write a test for `compute_grid_mapping`**
  Verify it can predict intermediate points given 4 corners.
- [ ] **Step 2: Implement `compute_grid_mapping(src_points, dst_points)`**
  Use `numpy.linalg.lstsq` to solve for an affine or simple homography matrix.
- [ ] **Step 3: Implement `project_grid(mapping, target_points)`**
  Apply the mapping to a list of Lab points to get Image points.
- [ ] **Step 4: Verify test passes**
- [ ] **Step 5: Commit**

### Task 3: GUI Controls & Overlay

**Files:**
- Modify: `MyPTV/myptv/extendedZolof/gui_initial_cal.py`
- Modify: `MyPTV/myptv/TsaiModel/gui_initial_cal.py`

- [ ] **Step 1: Add "Mark Grid", "Refresh", and "Accept Grid" buttons**
  Add them to the `init_cal_frame`.
- [ ] **Step 2: Implement `toggle_grid_mode`**
  Handle the button state and visual cues.
- [ ] **Step 3: Implement `draw_grid_overlay`**
  Draw Blue (control), Green (snapped), Yellow (projected) circles on the canvas.
- [ ] **Step 4: Commit**

### Task 4: Snapping & Iterative Refinement

**Files:**
- Modify: `MyPTV/myptv/extendedZolof/gui_initial_cal.py`
- Modify: `MyPTV/myptv/TsaiModel/gui_initial_cal.py`

- [ ] **Step 1: Implement `refresh_projection`**
  - Extract control points.
  - Call `compute_grid_mapping`.
  - Project all selected target points.
  - Snap projected points to `self.segmented` within 15px.
  - Update overlay.
- [ ] **Step 2: Update `markPoint` for Grid Mode**
  If `grid_mode` is ON, clicking a projected circle adds it to `control_points` instead of the standard marking flow.
- [ ] **Step 3: Commit**

### Task 5: Batch Acceptance & Verification

**Files:**
- Modify: `MyPTV/myptv/extendedZolof/gui_initial_cal.py`
- Modify: `MyPTV/myptv/TsaiModel/gui_initial_cal.py`

- [ ] **Step 1: Implement `accept_grid`**
  - Gather all Green (snapped) and Blue (control) points.
  - Add them to `self.point_list`.
  - Update `self.available_indices` and listbox.
  - Clear the grid overlay.
- [x] **Step 2: End-to-end verification**
  Manually test (or simulate) marking 4 corners of a Z-plane and accepting.
- [x] **Step 3: Commit**

### Task 6: Optional Parameter Support

**Files:**
- Modify: `MyPTV/myptv/extendedZolof/gui_initial_cal.py`
- Modify: `MyPTV/myptv/TsaiModel/gui_initial_cal.py`
- Modify: `MyPTV/example/workflow.py`

- [x] **Step 1: Add `blob_file` parameter to `gui_initial_cal.py`**
  Modify `__init__` to accept `blob_file` and load it if provided, prioritizing it over the default.
- [x] **Step 2: Add `blob_file` parameter to `workflow.py`**
  Update `initial_calibration` action to fetch `blob_file` from the `calibration` section of the YAML file.
- [x] **Step 3: Commit**

