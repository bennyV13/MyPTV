# Track: Web-Based Initial Calibration GUI Migration

## Phase 1: Research & Scaffolding
- [ ] Task: Research existing `gui_initial_cal.py` implementation and identify key functions to be exposed via the API.
- [ ] Task: Set up the React/TS project structure for the web GUI.
- [ ] Task: Define the API interface between the Python backend and the React frontend.
- [ ] Task: **Conductor - User Manual Verification 'Research & Scaffolding' (Protocol in workflow.md)**

## Phase 2: Backend Development (FastAPI)
- [ ] Task: Implement a FastAPI server to serve the frontend and provide API endpoints.
- [ ] Task: Create API endpoints for loading coordinate files and images.
- [ ] Task: Create API endpoints for executing the calibration algorithm and returning results.
- [ ] Task: Implement file system handlers for saving and loading calibration data.
- [ ] Task: **Conductor - User Manual Verification 'Backend Development' (Protocol in workflow.md)**

## Phase 3: Frontend Development (React/TS)
- [ ] Task: Implement the main dashboard and coordinate list view.
- [ ] Task: Build the interactive image viewer component with point-marking capability.
- [ ] Task: Implement the blob-snapping logic in the frontend (possibly using canvas or SVG).
- [ ] Task: Create the coordinate filtering and sorting interface.
- [ ] Task: **Conductor - User Manual Verification 'Frontend Development' (Protocol in workflow.md)**

## Phase 4: Integration & Feature Parity
- [ ] Task: Connect the frontend components to the backend API endpoints.
- [ ] Task: Verify real-time centroid detection and snapping between the backend and frontend.
- [ ] Task: Integrate the calibration execution and error display workflow.
- [ ] Task: Test and refine the data persistence and loading cycle.
- [ ] Task: **Conductor - User Manual Verification 'Integration & Feature Parity' (Protocol in workflow.md)**

## Phase 5: Deployment & Packaging
- [ ] Task: Create a single-command entry point (e.g., `myptv web-gui`) to launch the full application.
- [ ] Task: Ensure all dependencies are correctly handled for easy local installation.
- [ ] Task: Verify cross-platform (Windows/macOS/Linux) launching and browser compatibility.
- [ ] Task: **Conductor - User Manual Verification 'Deployment & Packaging' (Protocol in workflow.md)**

## Phase 6: Final Validation & Cleanup
- [ ] Task: Conduct a full end-to-end test of the calibration workflow using the web GUI.
- [ ] Task: Address any UI/UX inconsistencies or performance bottlenecks.
- [ ] Task: Update project documentation and user manual with the new web-GUI instructions.
- [ ] Task: **Conductor - User Manual Verification 'Final Validation & Cleanup' (Protocol in workflow.md)**