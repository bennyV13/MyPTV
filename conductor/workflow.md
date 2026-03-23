# Workflow: Calibration Optimization

## Development Lifecycle
1.  **Research**: Verify current calibration point file structure and `calibrate_extendedZolof` API. (Completed)
2.  **Design**: Brainstorm and approve the Greedy Iterative Optimization approach. (Completed)
3.  **Setup Track**: Initialize the conductor track for `calibration-optimization`. (In Progress)
4.  **Specification**: Create a detailed spec for the optimizer's core logic and I/O.
5.  **Implementation Plan**: Break down implementation into actionable tasks.
6.  **Execution**: Implement `optimize_calibration.py` and its tests.
7.  **Validation**: Test the script with provided example point files.
8.  **Completion**: Commit changes and finalize the track.

## Point Grouping Strategy
Columns are defined as sets of points sharing the same $(X, Z)$ lab coordinates but having different $Y$ coordinates. This matches the physical column structure of a water tank calibration target.
