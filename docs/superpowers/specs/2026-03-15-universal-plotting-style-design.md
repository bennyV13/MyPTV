# Design Document: Universal Plotting Style for Lagrangian Analysis

**Date:** 2026-03-15
**Status:** Approved (Draft)
**Author:** Gemini CLI

## 1. Problem Statement
The current `LagrangianAnalysis` class in `Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py` contains several plotting methods (`plot_msd`, `plot_pdf`, `plot_lvacf`). Each of these methods repeats a significant amount of boilerplate code for setting up figure size, applying grids, legends, labeling axes, and saving output. This duplication makes the code harder to maintain and results in visual inconsistencies if one plot's style is updated but others are not.

## 2. Proposed Approach: Plot Finalizer (Approach A)
We will implement a private helper method, `_apply_style`, within the `LagrangianAnalysis` class. This method will act as a "finalizer" that standardizes the visual appearance of all Lagrangian plots.

### 2.1 Component: `_apply_style(self, ax, title, xlabel, ylabel, save_path=None, logx=False, logy=False, color='#1f77b4', markersize=4)`
This method will be responsible for:
- Setting the title with a bold, standardized font size.
- Labeling the X and Y axes with consistent font sizes.
- Applying logarithmic scaling to X and/or Y axes when requested.
- Enabling a light-colored, standardized grid.
- Configuring a professional legend (shadow enabled, frame on).
- Removing the top and right "spines" for a modern, clean look.
- Applying `tight_layout` to ensure no labels are cut off.
- Saving the figure at high resolution (300 DPI) if a `save_path` is provided.

### 2.2 Standardized Defaults
To ensure a "research-grade" appearance across all plots, we will adopt the following defaults:
- **Figure Size:** `(8, 6)` inches.
- **DPI (Saving):** `300` DPI for publication-quality output.
- **Title Font Size:** `14` (bold).
- **Label Font Size:** `12`.
- **Primary Line Color:** `#1f77b4` (standard muted blue).
- **Marker Style:** `'o-'` (line with markers) with `markersize=4`.
- **Grid Alpha:** `0.3` (for subtlety).

## 3. Implementation Logic
For each plotting method (e.g., `plot_msd`):
1.  Initialize a figure and axis: `fig, ax = plt.subplots(figsize=(8, 6))`.
2.  Perform the core data plotting (e.g., `ax.plot(data, label='Data', ...)`).
3.  Call `self._apply_style(ax, title, xlabel, ylabel, save_path, logx, logy)` to finish the plot.

## 4. Testing & Validation
- **Visual Consistency:** Verify that MSD, PDF, and LVACF plots share identical font sizes, grid patterns, and legend styles.
- **Log Scaling:** Confirm that logarithmic plots (e.g., MSD) maintain correct grid and axis labeling.
- **Saving:** Verify that plots are saved as high-resolution PNGs when a path is provided.
- **Regression:** Ensure no existing analysis logic is broken by the refactoring.
