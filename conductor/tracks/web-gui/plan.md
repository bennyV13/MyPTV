# Implementation Plan: Web-Based GUI (Research Workstation)

## Phase 1: Modular Workstation Scaffolding
- [/] Implement Top Navigation with Categorized Dropdowns (Registry-based). [Implementation Plan: docs/superpowers/plans/2026-04-09-scaffolding.md](./../../docs/superpowers/plans/2026-04-09-scaffolding.md)
- [ ] Create Modular Layout with Main Workspace, Footer, and Collapsible Console.
- [ ] Set up Frontend Module Registry and Backend Action Dispatcher.

## Phase 2: Porting Initial Calibration GUI
- [ ] Refactor existing `App.tsx` into `InitialCalibrationView.tsx` module.
- [ ] Ensure all 24-point strategy features (snap, zoom, listbox) are functional.
- [ ] Verify communication with `calibrate_extendedZolof` backend.

## Phase 3: Operation Log & System View
- [ ] Implement Operation Log module reading from `myptvlog.jsonl`.
- [ ] Add Search, Filtering (Action/Camera), and Parameter Snapshot expansion.
- [ ] Create System Footer with live Project/Camera state.

## Phase 4: Multi-Action Dispatcher & State Sync
- [ ] Implement centralized `POST /api/run_action` in FastAPI.
- [ ] Integrate `params_file.yml` as the live source of truth for all modules.
- [ ] Stream real-time Python `stdout` to the Web Console.

## Phase 5: Progressive Porting
- [ ] Port Preprocessing actions (Segmentation, BG/EQ, Masking).
- [ ] Port Processing actions (Matching, Tracking, Smoothing).
- [ ] Port Analysis actions (Trajectories, Animations, Fibers).