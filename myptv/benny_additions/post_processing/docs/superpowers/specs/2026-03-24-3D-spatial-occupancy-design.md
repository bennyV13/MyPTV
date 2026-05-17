# 2026-03-24-3D-Spatial-Occupancy-Analysis-Design

## Goal
Develop a tool to verify if particle trajectories cover the experimental space using a Gaussian Integrated Occupancy (GIO) metric. This identifies "least visited" regions (dead zones) by balancing particle proximity and frequency.

## Architecture
- **Data Layer:** Parses `trajectories` files, filtering for valid IDs ($particle\_id \ge 0$) and spatial clipping.
- **Computation Layer:** Uses a 3D grid and Scipy `KDTree` to efficiently calculate Gaussian influence from particles to grid points.
- **Visualization Layer:** 
    - **Statistics:** Global $F$-statistic and occupancy distribution.
    - **3D Voids:** VTK export for "Shadow Map" rendering in Paraview.
    - **Slices:** Matplotlib-based XY heatmaps at multiple Z-depths.

## Data Specification
- **Input:** Space-separated `trajectories` file.
- **Columns:** `particle_id`, `x`, `y`, `z`, `ux`, `uy`, `uz`, `ax`, `ay`, `az`, `frame`.
- **Bounding Box:** $X \in [0, 100]$, $Y \in [0, 100]$, $Z \in [-50, 0]$.
- **Metric:** $S(\vec{g}) = \sum e^{-d^2/2\sigma^2}$ where $\sigma = 3\text{mm}$.

## Output Formats
1. **Summary Report:** Terminal output and PNG plot of occupancy distribution.
2. **VTK Map:** `.vtk` file containing the 3D scalar field $S$ for Paraview.
3. **Heatmap Slices:** Multi-panel PNG showing XY slices at $Z \in \{-45, -35, -25, -15, -5\}$.

## Success Criteria
- Accurately identifies regions with zero or low trajectory density.
- Efficiently handles large datasets (millions of points) using spatial indexing.
- Provides visual evidence of "holes" in the experimental volume.
