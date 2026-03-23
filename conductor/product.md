# Product Definition: Calibration Optimization

## Core Objective
To automate the discovery of the optimal subset of calibration points from `cam*_cal_points` files to minimize the initial calibration error in the `MyPTV` workflow.

## Success Criteria
1.  A standalone script, `optimize_calibration.py`, that processes existing calibration point files.
2.  Implementation of a "Greedy Iterative Optimization" algorithm with multiple random restarts.
3.  Support for user-defined point counts per "column" (e.g., picking 2, 3, or 4 points from each column).
4.  Generation of a new optimized point file (`cam*_cal_points_optimized`) that achieves a lower mean squared error (MSE) than a naive full set.
5.  Seamless integration with the `MyPTV` `extendedZolof` calibration modules.

## User Persona
A researcher performing Particle Tracking Velocimetry (PTV) in a water tank setup, dealing with complex refraction and seeking to achieve sub-pixel accuracy without manually testing every possible point combination.
