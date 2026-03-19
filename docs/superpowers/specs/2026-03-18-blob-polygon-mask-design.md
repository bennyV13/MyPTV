# Blob Polygon Mask Design Spec

**Date:** 2026-03-18
**Topic:** Blob Polygon Mask Generation
**Status:** Approved

## 1. Overview
This feature allows users to generate a binary mask image (`.tif`) based on the convex hull of a formation of segmented blobs. This is useful for defining a Region of Interest (ROI) that tightly follows the actual particle distribution, reducing noise in subsequent processing steps.

## 2. Requirements
- **Input:** A standard MyPTV blob file (space-separated text, columns 0=y, 1=x).
- **Output:** A binary mask image (`.tif`) where pixels inside the expanded polygon are 1 (white) and outside are 0 (black).
- Parameters:
    - `blob_file`: Path to the input blobs.
    - `resolution`: [width, height] of the camera image.
    - `padding`: Integer value in pixels to expand the polygon boundary.
    - `output_bit_depth`: Bit depth of the output mask (e.g., 8 or 16).
    - `save_name`: Path to save the resulting mask.
- Workflow: Integrated as a first-class step in `workflow.py`.
- Validation: Interactive Matplotlib plot showing blobs and the calculated polygon for user approval before saving.

## 3. Architecture & Components

### 3.1. Core Logic: `MyPTV/myptv/masking_mod.py`
A new module responsible for:
1.  **Loading Blobs:** Extracting $(y, x)$ coordinates.
2.  **Convex Hull:** Using `scipy.spatial.ConvexHull` to find the boundary vertices.
3.  **Polygon Expansion (Padding):**
    - For each vertex $V_i$, calculate the unit normal vectors $\hat{n}_{i-1,i}$ and $\hat{n}_{i,i+1}$ of the adjacent edges.
    - Expand the vertex along the average normal (bisector) by `padding` pixels.
    - Ensure vertices remain within image resolution [0, width/height].
4.  **Visualization:**
    - Plot all blobs as scatter points.
    - Plot the expanded polygon boundary as a line.
    - Provide a "Save" and "Abort" mechanism (e.g., via GUI button or keypress).
5.  **Rasterization:** Using `skimage.draw.polygon` to fill the mask.
6.  **Saving:** Using `skimage.io.imsave` to write the `.tif` file with the specified `output_bit_depth`.

### 3.2. Workflow Integration: `Data/20260315_frames/workflow.py`
- Add `create_blob_mask` to `allowed_actions`.
- Implement `self.create_blob_mask()` to bridge parameters to `masking_mod`.

### 3.3. Configuration: `Data/20260315_frames/params_file.yml`
- Add a new `create_blob_mask` section to define parameters:
    ```yaml
    - create_blob_mask:
        blob_file: Data/20260315_frames/blobs_cam1
        resolution: [2176, 2176]
        padding: 20
        output_bit_depth: 8
        save_name: Data/20260315_frames/mask_cam1.tif
    ```


## 4. Success Criteria
- The generated mask accurately represents the blob formation with the specified pixel padding.
- The user can visually verify the shape before any file is written.
- The workflow step executes seamlessly from the CLI.

## 5. Error Handling
- **File Not Found:** Handle missing blob files with clear error messages.
- **Insufficient Points:** Handle cases with < 3 blobs (where a convex hull cannot be formed) by logging a warning and skipping/aborting.
- **Invalid Resolution:** Ensure the resolution matches the camera parameters.
