# MyPTV Research & Development

## Project Overview
This project focuses on improving the **Particle Tracking Velocimetry (PTV)** workflow in the `MyPTV` library, specifically for a 4-camera setup monitoring a water tank. The primary goal is to minimize the "tedious" manual work required during the camera calibration phase while increasing the accuracy of the volumetric coordinate system.

## Core Objectives
1.  **Workflow Acceleration:** Reduce manual typing and precision clicking during initial calibration.
2.  **Accuracy Optimization:** Implement strategies to handle refraction (Air $\to$ Glass $\to$ Water) and achieve sub-pixel resolution.
3.  **Intelligent Automation:** Use geometry-aware algorithms to suggest and filter calibration points.

## Project Mandates
*   **Workspace Structure:** This project is part of a 3-sibling workspace (`MyPTV/`, `Data_and_analysis/`, and the Root for Project Management).
*   **Project Governance:** All planning, documentation, and `conductor` tracks are strictly managed at the **Root** of this repository. When "updating the plan" or "checking conductor," always refer to the root directory.
*   **Automatic Git Updates:** Always stage and commit local changes to the current branch as the final action before returning to the user. Use descriptive commit messages summarizing the fixes and improvements.
*   **Multi-Agent Development:** Use isolated Git Worktrees in `.worktrees/` for complex tasks or parallel sub-agents. Never work directly in the root directory for independent sub-tasks. Always use the `using-git-worktrees` skill for setup.

## Completed Improvements (`gui_initial_cal.py`)

### 1. Smart UI Elements
*   **Coordinate Listbox:** Automatically loads 3D coordinates from the `target_file`. Selecting a coordinate in the list auto-populates the Lab Space input fields (X, Y, Z).
*   **Auto-Advance & Removal:** After marking a point, the listbox automatically moves to the next coordinate and **removes the used point from the list**, preventing duplicates and streamlining the workflow.
*   **Live Point Counter:** Displays the real-time count of marked points and provides a visual recommendation (24 points) for stable calibration in water tank environments.
*   **Calibration Error Display:** Added a live label in the GUI that displays "Finished with error: X.XXX pixels" after running calibration, mirroring the terminal output for immediate feedback.

### 2. Geometric Algorithms & Interaction
*   **Blob Snapping:** When a user clicks near a dot, the cursor "snaps" to the exact centroid of the nearest detected blob. This ensures sub-pixel precision and eliminates "clicking errors."
*   **Predictive Zooming:** Selecting a point from the listbox now triggers an **automatic zoom-in** on the predicted image coordinates (if a rough calibration exists). The zoom level is user-configurable via a new GUI input field.
*   **Auto-Reset View:** The GUI automatically zooms back out to the full image view after a point is successfully marked, maintaining visual context.
*   **Optimal Points Filter:** A new algorithm that identifies the most important points (corners, edge-mids, and centers) for each Z-plane. It supports both full 3D grids and single-column/row planes.
*   **Multi-Axis Sorting:** Added the ability to instantly re-sort the coordinate list by **X, Y, or Z** to match the user's preferred marking order.
*   **Keyboard Efficiency:** Bound **`Shift+S`** to the "Mark Point" command, allowing for a rapid keyboard-and-mouse calibration workflow.

## Technical Setup
*   **Source Control:** Working on the `gemini-changes` branch.
*   **Remote:** Forked to `https://github.com/bennyV13/MyPTV`.
*   **Environment:** Installed in "editable mode" (`pip install -e .`) within a local `venv` to ensure all source code changes are instantly active.

## Recommended Calibration Strategy
For a water tank setup, we recommend the **24-Point Corner Strategy**:
*   **8 points per plane** (4 corners + 4 edge-mids) across **3 different depths** (Front, Middle, Back).
*   This provides the `extendedZolof` cubic polynomial model with enough data to compensate for refraction and lens distortion.

