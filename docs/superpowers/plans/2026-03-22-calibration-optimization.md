# Calibration Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a script to find the optimal subset of calibration points (k per column) to minimize MSE.

**Architecture:** A standalone script `optimize_calibration.py` using a greedy iterative search with multiple random restarts.

**Tech Stack:** Python, NumPy, MyPTV (extendedZolof).

---

### Task 1: PointManager and Grouping

**Files:**
- Create: `MyPTV/myptv/extendedZolof/optimize_calibration.py`
- Create: `MyPTV/tests/test_calibration_optimization.py`

- [ ] **Step 1: Write the failing test for grouping**
- [ ] **Step 2: Implement `PointManager` with `get_groups` method**
- [ ] **Step 3: Verify test passes**
- [ ] **Step 4: Commit**

### Task 2: OptimizerCore and Greedy Search

**Files:**
- Modify: `MyPTV/myptv/extendedZolof/optimize_calibration.py`
- Modify: `MyPTV/tests/test_calibration_optimization.py`

- [ ] **Step 1: Implement `OptimizerCore` with `greedy_step` logic**
- [ ] **Step 2: Implement `run_local_optimization` (convergence loop)**
- [ ] **Step 3: Write tests using a small synthetic point set**
- [ ] **Step 4: Verify tests pass**
- [ ] **Step 5: Commit**

### Task 3: Global Multi-Start and CLI

**Files:**
- Modify: `MyPTV/myptv/extendedZolof/optimize_calibration.py`

- [ ] **Step 1: Implement `run_global_optimization` with random restarts**
- [ ] **Step 2: Implement CLI using `argparse`**
- [ ] **Step 3: Add I/O to save `cam*_cal_points_optimized`**
- [ ] **Step 4: Test end-to-end with an example point file**
- [ ] **Step 5: Commit**
