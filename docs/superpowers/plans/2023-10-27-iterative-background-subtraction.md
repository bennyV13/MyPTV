# Iterative Background Calculation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an iterative background calculation algorithm in `myptv` to reduce residue artifacts by repeatedly calculating the median of residuals.

**Architecture:** Modify the `calculate_BG_image` function in `segmentation_mod.py` to support multiple iterations. In each iteration, the background is calculated as the median of the current residuals (Images - Cumulative_BG), and the result is added to the Cumulative_BG. Update the `workflow.py` to expose these new parameters (`iterations`) through the YAML configuration.

**Tech Stack:** Python, NumPy, Scikit-Image, YAML.

---

### Task 1: Enhance `calculate_BG_image` in `segmentation_mod.py`

**Files:**
- Modify: `myptv/segmentation_mod.py`

- [ ] **Step 1: Update `calculate_BG_image` signature and implementation**
Modify the function to support `iterations` and use `numpy.median` for calculation. Ensure residuals are signed (float) during the process.

```python
def calculate_BG_image(dir_name, extension, savename, N_img=200,
                       raw_format=False, iterations=1):
    '''
    Calculates a background image using an iterative median approach and 
    saves it on the disk.
    '''
    import numpy as np
    from skimage import io
    import tqdm
    import os

    if raw_format == False:
        imread_func = lambda x: io.imread(x)
    else:
        import rawpy
        imread_func = lambda x: rawpy.imread(x).raw_image
        
    BG_image_paths = get_img_list(dir_name, extension, N_img=N_img)
    
    # Load images into memory as float32 to allow signed residuals
    images = []
    for path in tqdm.tqdm(BG_image_paths, desc='Loading images for BG'):
        img = imread_func(path).astype('float32')
        images.append(img)
    images = np.array(images)
    
    # Initial background calculation (Iteration 1)
    BG_total = np.median(images, axis=0)
    
    # Iterative refinement (Iteration 2+)
    for i in range(iterations - 1):
        desc = f'Refining BG (iteration {i+2}/{iterations})'
        residuals = images - BG_total
        BG_i = np.median(residuals, axis=0)
        BG_total += BG_i
        
    # Convert back to original dtype (assuming uint8 or uint16 based on input)
    final_BG = BG_total.astype(imread_func(BG_image_paths[0]).dtype)
    
    # saving
    io.imsave(savename, final_BG, check_contrast=False)
    return final_BG
```

- [ ] **Step 2: Commit changes**

```bash
git add myptv/segmentation_mod.py
git commit -m "feat(segmentation): implement iterative median background calculation"
```

---

### Task 2: Update `workflow.py` to expose `iterations` parameter

**Files:**
- Modify: `myptv/workflow.py`

- [ ] **Step 1: Update `do_calculate_BG_image` to read `iterations`**
Modify the method to fetch the `iterations` parameter from the `calculate_BG_image` section of the YAML file.

```python
    def do_calculate_BG_image(self):
        '''
        Calculates and save static BG image
        '''
        from myptv.segmentation_mod import calculate_BG_image
        import os
        
        dirname = self.get_param('calculate_BG_image', 'images_folder')
        ext = self.get_param('calculate_BG_image', 'image_extension')
        raw_format = self.get_param('calculate_BG_image', 'raw_format')
        N_img = self.get_param('calculate_BG_image', 'N_img')
        savename = self.get_param('calculate_BG_image', 'save_name')
        
        # New parameter
        try:
            iterations = self.get_param('calculate_BG_image', 'iterations')
            if iterations is None: iterations = 1
        except:
            iterations = 1
        
        if savename is not None:
            # ... (existing check code)
        
        calculate_BG_image(dirname, ext, savename, N_img=N_img,
                       raw_format=raw_format, iterations=iterations)
```

- [ ] **Step 2: Update internal `calculate_BG_image` in `do_segmentation`**
Ensure the background calculation triggered during the segmentation workflow also supports iterations if `remove_background: True` and no pre-calculated image is provided.

```python
        # inside do_segmentation method
        try:
            bg_iterations = self.get_param('segmentation', 'bg_iterations')
            if bg_iterations is None: bg_iterations = 1
        except:
            bg_iterations = 1

        def calculate_BG_image(dirname, extension, iterations=1):
            # ... (updated internal function logic similar to Task 1 but returning in-memory)
            import numpy as np
            # ... (implement iterative median logic here)
            return BG_total
```

- [ ] **Step 3: Commit changes**

```bash
git add myptv/workflow.py
git commit -m "feat(workflow): add iterations support to background calculation"
```

---

### Task 3: Verification

- [ ] **Step 1: Create a test reproduction script**
Create a script that generates dummy images with a static background and moving particles, then verifies that `calculate_BG_image` converges correctly.

- [ ] **Step 2: Run verification**
Run the script and check the output image.

- [ ] **Step 3: Clean up**
Remove the test script.
