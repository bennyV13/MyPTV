# Plan: Batch Background Image Calculation

### Objective
Implement a batch processing capability for background image calculation (`calculate_BG_image_batch`) that automatically processes multiple recordings and cameras, saving the results in a flattened output directory structure.

### Key Files & Context
- **`myptv/segmentation_mod.py`**: The core segmentation module containing the existing `calculate_BG_image` function.
- **`myptv/workflow.py`**: The workflow manager that reads parameters from the configuration file and routes to the correct actions.

### Implementation Steps

#### Step 1: Implement `calculate_BG_image_batch` in `segmentation_mod.py`
Add a new function `calculate_BG_image_batch` that takes `recordings_dir` and `output_dir` as inputs, along with parameters like `extension`, `N_img`, `raw_format`, and `iterations`.
The logic will:
1. Ensure the `output_dir` exists.
2. Iterate through all folders in `recordings_dir` that start with "rec" (case-insensitive).
3. Inside each recording folder, iterate through all subfolders that start with "cam" (case-insensitive).
4. For each camera, create the corresponding recording folder in the `output_dir` (e.g., `output_dir/rec01/`).
5. Run the existing background calculation logic (median subtraction) on the camera's images.
6. Save the resulting background image to `output_dir/recXX/<CamName>_BG.tif` (e.g., `output_dir/rec01/Cam1_BG.tif`).

#### Step 2: Add `calculate_BG_image_batch` to `workflow.py`
1. Add `'calculate_BG_image_batch'` to the `self.allowed_actions` list in the `workflow` class `__init__` method.
2. Add a new `elif action == 'calculate_BG_image_batch':` block in `__init__` that calls `self.do_calculate_BG_image_batch()`.
3. Implement the `do_calculate_BG_image_batch(self)` method to:
   - Extract `recordings_dir`, `output_dir`, `image_extension`, `raw_format`, `N_img`, and `iterations` from the `calculate_BG_image_batch` section of the parameter file.
   - Import and call the new `calculate_BG_image_batch` function from `segmentation_mod.py` using these parameters.

### Verification & Testing
- Use a test recording directory structure to verify the traversal logic.
- Run the workflow script with a mock `params_file.yml` configured for `calculate_BG_image_batch` to ensure the backgrounds are processed and saved in the correct `output_dir` structure with the correct naming convention (`<CamName>_BG.tif`).
- Verify that parameters like `iterations` and `raw_format` are properly passed down to the underlying calculation logic.