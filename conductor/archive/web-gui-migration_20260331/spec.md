# Track: Web-Based Initial Calibration GUI Migration

## Overview
This track involves migrating the existing `gui_initial_cal.py` graphical user interface from its current Python-based implementation to a web-based environment using **React/TS**. The primary goal is to ensure visual consistency and cross-platform compatibility across all computers while maintaining full feature parity with the current system.

## Functional Requirements
- **Feature Parity**: Full migration of all existing features from the current GUI:
    - **Interactive Coordinate Marking**: Selecting 3D coordinates from the target file and marking them on the 2D image.
    - **Blob Snapping & Centroid Detection**: Real-time cursor snapping to detected blob centroids with sub-pixel precision.
    - **Calibration Execution & Error Display**: Initiating the calibration process (calling the Python backend) and displaying the resulting error in the GUI.
    - **Data Persistence**: Saving marked points and calibration parameters back to the filesystem.
    - **Coordinate Filtering & Sorting**: Ability to filter and sort the 3D coordinate list by X, Y, or Z axes.
- **Python Integration**: The web GUI must communicate with a Python backend (presumably using a lightweight web server like FastAPI or Flask) to handle file I/O and the heavy lifting of the calibration algorithms.
- **Easy Deployment**: The solution must be easily deployable for users who primarily work with Python (e.g., via a single command or script that launches both the backend and frontend).

## Non-Functional Requirements
- **Consistency**: Visual and functional consistency across different operating systems and browsers.
- **Performance**: High interactivity for blob snapping and zooming to maintain the "rapid" workflow.
- **Maintainability**: Clean, modular code using TypeScript and React.

## Acceptance Criteria
- [ ] Users can launch the web-based GUI from a single Python command.
- [ ] The web GUI accurately mirrors the functionality and workflow of the existing `gui_initial_cal.py`.
- [ ] All saving and loading operations work correctly on the local filesystem via the Python backend.
- [ ] Blob-snapping and zooming feel as responsive as the original implementation.
- [ ] Calibration results (pixel errors) are correctly retrieved and displayed.

## Out of Scope
- **Hosted Cloud Deployment**: The focus is strictly on a local-only laboratory environment.
- **New Data Visualization Features**: Beyond parity, no new 3D visualizations or dashboards are planned for this initial migration.
- **Predictive Zooming & View Reset**: This feature will not be part of the initial web-based GUI migration.