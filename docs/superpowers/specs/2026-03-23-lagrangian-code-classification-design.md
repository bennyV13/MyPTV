# Design: Lagrangian Analysis Code Classification

A classification of the Lagrangian PTV data analysis scripts in `analyzing_softwares_copy/analyzing_softwares/velocity_field_lagrangian`.

## 1. Functional Classification (By Purpose)

Categorizes scripts by their primary technical role within the analysis library.

### Core Logic & Abstractions
The fundamental building blocks and base classes for the entire Lagrangian framework.
- **`voxel_class.py`**: Defines the `Voxel` base class and concrete types (`CubeVoxel`, `CylinderVoxel`). Contains the heavy logic for statistics calculation (`stats_1`, `stats_2`, `stats_3`).
- **`voxel_space.py`**: Generators for Cartesian and cylindrical grids. Responsible for creating the initial geometry of the ROI.

### Data Ingestion & Conversion
Scripts for moving data into the pipeline and between different formats.
- **`traj2npy.py`**: Loads raw trajectory data, cleans outliers (Z-score/MAD), and saves it as a consolidated `.npy` array for fast loading.
- **`traj2npy_multiple.py`**: Similar to `traj2npy`, but processes and merges multiple files.
- **`pickle2csv.py`**: Converts a pickled snapshot of voxels into a flat CSV, suitable for import into other tools (Excel, Origin, etc.).

### Processing Pipeline
The sequential "factory" for processing Lagrangian data from trajectories into statistics.
- **`divide_points_to_cube_voxels.py`**: High-performance point assignment. It builds the grid, takes the trajectory data, and assigns each point to a voxel.
- **`calculate_stats.py`**: The primary processing script. It runs the multi-phase statistics pipeline (means, spatial derivatives, turbulence metrics, and **collision rates**).
- **`remove_zero_vox.py`**: Post-processing tool to clean up the voxel grid by removing cells with no points or low coverage.

### Advanced Analysis
Specialized tools for deeper insight into specific physics or comparative analysis.
- **`voxels_compare.py`**: Compares two different voxel distributions or analysis runs.
- **`voxel_class.py` (Macros)**: Support for cross-voxel macro calculations.
- **`add_collision_rate.py` (DEPRECATED)**: Historically used to add collision rates post-calculation. This logic is now integrated directly into `calculate_stats.py` and `voxel_class.py`.

### Visualization & Utilities
Tools for creating plots, profiles, and maintaining consistent visual styles.
- **`plot_lagrangian_results.py`**: The main plotting script. Generates radial/height profiles and volume fraction (coverage) plots.
- **`ori_plotter.py`**: Contains reusable plotting utilities, consistent style configuration, and vorticity direction visualizations.

## 2. Workflow Classification (By Sequence)

The recommended step-by-step path for running a complete analysis.

### Step 1: Ingestion
Convert your raw PTV results (trajectories) into an optimized binary format for faster processing.
*   **Run:** `traj2npy.py` (or `traj2npy_multiple.py`).
*   **Output:** `smoothed_trajectories.npy`.

### Step 2: Partitioning
Define your analysis volume (ROI) and grid resolution. Assign your points to their corresponding spatial cells.
*   **Run:** `divide_points_to_cube_voxels.py`.
*   **Output:** `voxels_points.pkl`.

### Step 3: Computation
Run the main statistical pipeline to compute means, fluctuations, and turbulence parameters.
*   **Run:** `calculate_stats.py`.
*   **Output:** `voxels_stats.pkl`.

### Step 4: Refinement (Optional)
Prune low-data or empty voxels to clean up your results before plotting.
*   **Run:** `remove_zero_vox.py`.
*   **Output:** A refined `voxels_stats.pkl`.

### Step 5: Visualization & Export
Generate your final analysis plots and export data for external use.
*   **Run:** `plot_lagrangian_results.py` (for profiles).
*   **Run:** `pickle2csv.py` (to export to CSV).
