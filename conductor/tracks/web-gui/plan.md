# Implementation Plan: Web-Based GUI

## Phase 1: Setup & Scaffolding
- [ ] Initialize React (TS) frontend with Vite.
- [ ] Set up FastAPI backend.
- [ ] Define API endpoints for image loading and coordinate marking.

## Phase 2: Core Functionality
- [ ] Implement image viewer with zoom capabilities.
- [ ] Develop coordinate list and point selection logic.
- [ ] Port blob-snapping algorithm to backend/frontend.

## Phase 3: Calibration Integration
- [ ] Integrate with `MyPTV` calibration modules (`TsaiModel`, `extendedZolof`).
- [ ] Implement live error display after calibration.

## Phase 4: Refinement & Validation
- [ ] Ensure feature parity with `gui_initial_cal.py`.
- [ ] Optimize performance for high-resolution images.