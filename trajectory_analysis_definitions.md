# MyPTV Trajectory Analysis Definitions

This document summarizes the key functions and classes available in the `MyPTV` library for analyzing trajectory (Lagrangian) data.

## 1. Lagrangian Analysis Tools
**Location:** `MyPTV/myptv/data_analysis/analysis_tools.py`

These functions provide fundamental tools for extracting statistics and profiles from trajectory data.

*   `load_trajs_as_arrays(fname)`: Loads a trajectory file (tab-separated) and returns a list of NumPy arrays, each representing a single trajectory sorted by frame.
*   `get_velocity_list(traj_list, kind='x')`: Returns a flat list of all velocity samples for a given component ('x', 'y', 'z', or 'KE' for kinetic energy).
*   `get_trajectory_velocities(traj_list, kind='x')`: Returns a nested list where each sublist is the velocity time series of one trajectory.
*   `get_velocity_mean_std(traj_list, kind='x')`: Returns the mean and standard deviation of a velocity component across all trajectories.
*   `get_trajectory_velocity_increments(traj, kind='x')`: Returns temporal increments of velocity ($V(t+\tau) - V(t)$) for various time lags $\tau$.
*   `get_mean_std_time_series(traj_list, kind='x')`: Returns statistics (sample count, mean, std) as a function of time frames.
*   `get_mean_velocity_profiles(traj_list, start, stop, nbins, direction, kind)`: Calculates a spatial profile (e.g., mean velocity vs. Z-coordinate).
*   `get_Lagrangian_autocorrelation(traj_list, kind='x')`: Calculates the velocity autocorrelation function for Lagrangian particles.
*   `get_pairs(traj_list)`: Identifies common time instances between pairs of trajectories to calculate relative positions and velocities.

## 2. Relative Motion & Pairing
**Location:** `MyPTV/myptv/data_analysis/getting_pairs.py`

Specialized script for obtaining relative trajectories between particle pairs.

*   `get_pairs(traj_list, Np=100)`: An optimized version of the pairing algorithm that processes trajectories in groups (`Np`) to increase speed. It returns relative positions, velocities, and accelerations.

## 3. Data Preparation (Smoothing)
**Location:** `MyPTV/myptv/traj_smoothing_mod.py`

Before analysis, trajectories are typically smoothed to reduce noise and calculate derivatives (velocity/acceleration).

*   `class smooth_trajectories`: A class used to filter raw tracking results. It uses Savitzky-Golay filters or similar methods to provide clean Lagrangian data.

## 4. Quality Assessment
**Location:** `MyPTV/myptv/makePlots/quality_estimators.py`

Tools to assess the reliability of the tracked data before deep analysis.

*   `class check_matching`: Visualizes triangulation uncertainties and assesses the quality of stereo matching.
*   `get_particle_disparity`: Measures the distance between a particle's 3D projection and its 2D blob detection.
*   `plot_disparity_histogram`: Visualizes the distribution of matching errors.

## 5. Visualization
**Location:** `MyPTV/myptv/makePlots/plot_trajectories.py`

*   `class animate_trajectories`: Provides 3D animation of particle movements.
*   `plot_matched_trajs_over_images.py`: Overlays 3D trajectories back onto the raw camera frames for verification.
