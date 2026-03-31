# Track: Web-Based Initial Calibration GUI Migration

## Phase 1: Research & Scaffolding
- [x] Task: Research existing `gui_initial_cal.py` implementation and identify key functions to be exposed via the API.
- [x] Task: Set up the React/TS project structure for the web GUI.
- [x] Task: Define the API interface between the Python backend and the React frontend.
- [x] Task: **Conductor - User Manual Verification 'Research & Scaffolding' (Protocol in workflow.md)**

## Phase 2: Backend Development (FastAPI)
- [x] Task: Implement a FastAPI server to serve the frontend and provide API endpoints.
- [x] Task: Create API endpoints for loading coordinate files and images.
- [x] Task: Create API endpoints for executing the calibration algorithm and returning results.
- [x] Task: Implement file system handlers for saving and loading calibration data.
- [x] Task: **Conductor - User Manual Verification 'Backend Development' (Protocol in workflow.md)**

## Phase 3: Frontend Development (React/TS)
- [x] Task: Implement the main dashboard and coordinate list view.
- [x] Task: Build the interactive image viewer component with point-marking capability.
- [x] Task: Implement the blob-snapping logic in the frontend (possibly using canvas or SVG).
- [x] Task: Create the coordinate filtering and sorting interface.
- [x] Task: **Conductor - User Manual Verification 'Frontend Development' (Protocol in workflow.md)**

## Phase 4: Integration & Feature Parity
- [x] Task: Connect the frontend components to the backend API endpoints.
- [x] Task: Verify real-time centroid detection and snapping between the backend and frontend.
- [x] Task: Integrate the calibration execution and error display workflow.
- [x] Task: Test and refine the data persistence and loading cycle.
- [x] Task: **Conductor - User Manual Verification 'Integration & Feature Parity' (Protocol in workflow.md)**

## Phase 5: Deployment & Packaging
- [x] Task: Create a single-command entry point (e.g., `myptv web-gui`) to launch the full application.
- [ ] Task: Ensure all dependencies are correctly handled for easy local installation.
- [ ] Task: Verify cross-platform (Windows/macOS/Linux) launching and browser compatibility.
- [ ] Task: **Conductor - User Manual Verification 'Deployment & Packaging' (Protocol in workflow.md)**

## Phase 6: Full Workflow Integration & Parity
- [x] Task: Integrate `params_file.yml` to pre-load GUI settings (Threshold, ROI, etc.).
- [x] Task: Implement a "Web Console" in the GUI to display real-time terminal feedback from Python.
- [x] Task: Fix blob visualization (ensure green squares appear correctly after segmentation).
- [x] Task: Add `web-gui` command to the main `myptv` CLI entry point (via `workflow.py`).
- [x] Task: **Conductor - User Manual Verification 'Full Workflow Integration' (Protocol in workflow.md)**

## Phase 7: Final Validation & Cleanup
- [ ] Task: Conduct a full end-to-end test of the calibration workflow using the web GUI.
- [ ] Task: Address any UI/UX inconsistencies or performance bottlenecks.
- [ ] Task: Update project documentation and user manual with the new web-GUI instructions.
- [ ] Task: **Conductor - User Manual Verification 'Final Validation & Cleanup' (Protocol in workflow.md)**