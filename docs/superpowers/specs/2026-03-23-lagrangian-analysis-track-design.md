# Design: Lagrangian Analysis Track in Conductor

This track implements a full Lagrangian data analysis pipeline within the `conductor` framework, focused on processing smoothed PTV trajectories into volumetric statistics.

## 1. Track Metadata
- **Track ID**: `lagrangian-analysis`
- **Name**: Lagrangian Data Analysis Pipeline
- **Status**: Active
- **Goal**: Automate the transition from PTV trajectory data to high-quality volumetric statistics and profiles.

## 2. Track Structure
The track will be located at `conductor/tracks/lagrangian-analysis/` and will include:
- **`index.md`**: High-level overview, workflow checklist, and task tracking.
- **`spec.md`**: Technical specification for each analysis step, including required parameters and expected outputs.
- **`metadata.json`**: Machine-readable configuration for the track.

## 3. Workflow (Full Refinement Pipeline)
The analysis will follow a sequential path:

### Step 1: Ingestion (`traj2npy.py`)
- **Action**: Load `smoothed_trajectories.npy` (or equivalent) and ensure it's in the optimized binary format.
- **Role**: Prepares data for high-speed spatial partitioning.

### Step 2: Partitioning (`divide_points_to_cube_voxels.py`)
- **Action**: Define the grid geometry (Cartesian ROI) and assign trajectory points to voxels.
- **Output**: `voxels_points.pkl`.

### Step 3: Statistical Computation (`calculate_stats.py`)
- **Action**: Execute the multi-phase statistics pipeline (means, spatial derivatives, turbulence metrics, and **mean collision rates**).
- **Output**: `voxels_stats.pkl`.

### Step 4: Data Refinement (`remove_zero_vox.py`)
- **Action**: Filter out empty or low-density voxels to ensure statistical significance in the final output.
- **Output**: Refined `voxels_stats.pkl`.

### Step 5: Visualization & Export
- **Export**: `pickle2csv.py` for CSV generation.
- **Visualization**: `plot_lagrangian_results.py` for generating radial/vertical profiles.

## 4. Tech Stack & Dependencies
- **Source Scripts**: `analyzing_softwares_copy/analyzing_softwares/velocity_field_lagrangian/`
- **Environment**: Local `venv` with `MyPTV` dependencies.
- **Data Source**: Lagrangian smoothed trajectories.
