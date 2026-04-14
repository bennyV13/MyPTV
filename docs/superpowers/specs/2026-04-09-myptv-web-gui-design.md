# Specification: MyPTV Web-based Research Workstation

## Goal
To migrate the comprehensive MyPTV workflow (20+ actions) into a modern, multi-page web environment using React (TypeScript) and FastAPI, while maintaining the Python engine as the authoritative source of truth.

## Architecture

### 1. Python Engine (Backend)
- **Framework**: FastAPI.
- **Integration**: Direct import of MyPTV core modules (`workflow`, `camera`, `tracking`, etc.).
- **Action Dispatcher**: A central `POST /api/run_action` endpoint that maps `action_id` to Python functions.
- **State Management**:
    - `params_file.yml`: The primary configuration source of truth, synced in real-time.
    - `myptvlog.jsonl`: Used for the Operation Log and parameter snapshots.
- **Log Streaming**: Captures `stdout`/`stderr` from the MyPTV engine and streams it to the frontend via a log buffer or WebSocket.

### 2. Interactive Frontend
- **Framework**: React (TypeScript) + Vite + Vanilla CSS.
- **Layout**: 
    - **Top Navigation Bar**: Categorized dropdown menus (Preprocessing, Calibration, Processing, Analysis).
    - **Main Workspace**: Dynamic area that loads the active module's view.
    - **Persistent Footer**: Status indicators (Project Path, Active Camera, Server Status).
    - **Collapsible Console**: Real-time terminal output from the Python engine.
- **Module Registry**: A centralized `src/modules.ts` file that defines the navigation structure and component mapping, allowing for easy rearrangement of the UI.

## Core Modules & Features

### Preprocessing
- **Segmentation**: Image thresholding and blob detection with ROI support.
- **BG/EQ Calculation**: Background subtraction and equalization map generation.
- **Blob Masking**: Tool to create and manage exclusion masks.

### Calibration
- **Initial GUI**: Image viewer with zoom, sub-pixel blob-snapping, and 3D coordinate listbox.
- **Final Calibration**: Global multi-camera optimization.
- **Error Analysis**: Visual and statistical reports on calibration residuals.

### Processing
- **Matching/Tracking**: Core PTV algorithms for trajectory reconstruction.
- **Smoothing/Stitching**: Post-processing tools for data refinement.

### Analysis & System
- **Trajectory Visualization**: 2D/3D plots (Matplotlib/Plotly) and interactive animations.
- **Operation Log**: Searchable and filterable history of all past runs using `myptvlog.jsonl`, including parameter snapshots.
- **Fibers**: Specialized tools for fiber orientation analysis.

## Technical Standards
- **Precision**: Sub-pixel accuracy for all image interactions.
- **Reproducibility**: All GUI actions must be reflected in the project's parameters and logs.
- **Maintainability**: Modular design allowing new MyPTV actions to be added by registering a new action ID and component.

## Success Criteria
- Feature parity with all 20+ `allowed_actions` in the MyPTV workflow.
- Real-time feedback and log streaming from the Python engine.
- A clean, professional, and customizable navigation structure.
- Full search/filter capability for the operation log.