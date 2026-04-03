# Track: Lagrangian Data Analysis Pipeline

This track manages the sequential processing of stitched PTV trajectories into volumetric Lagrangian statistics.

## Current Status
- **Progress**: 100%
- **Current Step**: Completed

## Workflow Checklist

### Phase 1: Pre-processing & Ingestion
- [x] **Step 1: Trajectory Filtering** - Remove irrelevant points (ID -1, zero velocity) using `remove_irrelevent.py`.
- [x] **Step 2: Velocity Conversion** - Convert mm/frame to mm/sec (FPS=25) using `convert_velocity.py`.
- [x] **Step 3: Binary Ingestion** - Convert trajectories to `.npy` format using `traj2npy.py`.

### Phase 2: Spatial Partitioning
- [x] **Step 4: Voxel Generation** - Create ROI grid geometry using `voxel_space.py`.
- [x] **Step 5: Point Partitioning** - Assign points to voxels using `divide_points_to_cube_voxels.py`.

### Phase 3: Statistical Analysis
- [x] **Step 6: Calculate Statistics** - Compute means, Reynolds stresses, and collision rates using `calculate_stats.py`.
- [x] **Step 7: Data Refinement** - Remove low-significance voxels using `remove_zero_vox.py`.

### Phase 4: Export & Visualization
- [x] **Step 8: Export to CSV** - Convert results to CSV for external analysis using `pickle2csv.py`.
- [x] **Step 9: Plotting** - Generate profiles and fields using `plot_lagrangian_results.py`.
    - [Implementation Plan: docs/superpowers/plans/2026-03-15-universal-plotting-style.md](docs/superpowers/plans/2026-03-15-universal-plotting-style.md) (COMPLETED: Added `_apply_style` for visual consistency across all Lagrangian plots).

## Final Results Summary
The Lagrangian analysis was successfully performed on the `trajecotries_stitched` dataset.

### Key Outputs (in `Data_and_analysis/Analysis/20260315_analysis/lagrangian_results/`):
- `cleaned_trajectories.csv`: Filtered and velocity-converted (mm/sec) data.
- `voxels_stats.pkl`: Snapshot of non-empty voxels with all computed statistics.
- `voxels_stats.csv`: Flattened statistics for all contributing voxels.
- `plot_epsilon_bottom.png` & `plot_epsilon_center.png`: Vertical and radial energy dissipation profiles.
- `plot_count_bottom.png` & `plot_count_center.png`: Voxel occupancy (data density) profiles.

### Analysis Statistics:
- **Total Points Filtered**: 56,968 (after ROI and ID filtering).
- **Voxel Grid**: 5,832 total voxels, 2,951 with significant data.
- **ROI**: X[0, 100], Y[0, 100], Z[-50, 0].
