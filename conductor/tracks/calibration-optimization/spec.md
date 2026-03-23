# Specification: Calibration Optimization

## Goal
A script that finds a subset of calibration points (e.g., 2, 3, or 4 points per column) that yields the lowest possible calibration error (MSE) using the `MyPTV` `extendedZolof` model.

## Algorithm: Multi-Start Greedy Search

1.  **Grouping**: Parse the `cam*_cal_points` file and group points into "columns" where $X$ and $Z$ are the same but $Y$ is different.
2.  **Initialization**: 
    - Randomly select $k$ points from each column to form a starting set.
    - Set `best_overall_error` to infinity and `best_overall_points` to empty.
3.  **Local Optimization (Greedy Loop)**:
    - Loop through each column:
        - For the current column, try **all possible $\binom{N_c}{k}$ combinations** of $k$ points (where $N_c$ is points in the current column).
        - Keep the other columns fixed to their current $k$ points.
        - Calculate the calibration error (MSE) for each combination in the current column using `calibrate_extendedZolof`.
        - Update the current column's selection to the one that gave the lowest MSE.
    - Repeat the loop across all columns until the `total_mse` stops decreasing (convergence).
4.  **Global Iteration**: 
    - Run the entire "Local Optimization" process $M$ times (e.g., $M=10$) from different random starting seeds.
    - Store the result with the absolute lowest MSE found.

## Input/Output

### Input
- `cam_points_file`: Path to the existing `cam*_cal_points` file.
- `k`: Number of points to pick per column (default 3).
- `M`: Number of random restarts (default 10).
- `cam_name`: Name of the camera (to load corresponding camera instance).

### Output
- `cam*_cal_points_optimized`: A new file containing the optimized subset of points.
- `calibration_optimization_log.txt`: A report showing the original error vs. the optimized error and the number of iterations performed.

## Components

### `PointManager`
- Responsible for parsing point files and grouping them by $(X, Z)$.
- Handles the selection and replacement of points during the greedy search.

### `OptimizerCore`
- Implements the greedy search logic.
- Interfaces with `calibrate_extendedZolof.mean_squared_err()`.

### `MainCLI`
- Provides a command-line interface using `argparse` to run the optimization.
