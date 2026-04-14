# Specification: Web-Based GUI

## Goal
To migrate the existing `gui_initial_cal.py` functionality to a modern web-based environment for a better user experience and cross-platform compatibility.

## Functional Requirements
1.  **Image Display**: Load and display calibration images (`cam*`).
2.  **Coordinate Selection**: Select and mark 3D coordinates from a listbox (sourced from `target_file`).
3.  **Blob Snapping**: Automatically snap to the nearest blob centroid when a user clicks on the image.
4.  **Zooming**: Support zooming into specific coordinates.
5.  **Calibration**: Trigger the calibration process (e.g., `extendedZolof`) from the UI.
6.  **Progress Tracking**: Show real-time feedback on marked points and calibration errors.

## Technical Requirements
- **Frontend**: React (TypeScript) + Vite + Vanilla CSS.
- **Backend**: FastAPI for image processing and calibration logic.
- **Integration**: Communication between frontend and backend via REST API.