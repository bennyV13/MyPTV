# Copy BG and EQ Functions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Copy `do_apply_BG_and_EQ` and `do_calculate_BG_and_EQ` from the source `workflow.py` to the target `workflow.py` and ensure they are properly integrated and compatible with `myptv`.

**Architecture:** The functions will be added as methods to the `workflow` class in the target `workflow.py`. The `allowed_actions` list and the action dispatch logic in `__init__` will be updated to include these new actions.

**Tech Stack:** Python, MyPTV library, NumPy, Scikit-Image, PyYAML, Pandas.

---

### Task 1: Research and Verify Compatibility

**Files:**
- Source: `Data_and_analysis/Analysis/analyzing_softwares_copy/workflow.py`
- Target: `Data_and_analysis/20260315_frames/workflow.py`
- Library: `MyPTV/myptv/segmentation_mod.py`

- [x] **Step 1: Read source functions** (Already done)
- [x] **Step 2: Read target workflow class** (Already done)
- [x] **Step 3: Verify library functions availability** (Already done)
- [ ] **Step 4: Verify `ActionLogger` compatibility**
    - Ensure the new actions can be logged using the existing `ActionLogger` in the target file.

### Task 2: Update `workflow.__init__` in Target File

**Files:**
- Modify: `Data_and_analysis/20260315_frames/workflow.py`

- [ ] **Step 1: Update `self.allowed_actions`**
    Add `'calculate_BG_and_EQ'` and `'apply_BG_and_EQ'` to the list.

- [ ] **Step 2: Update action dispatch logic**
    Add `elif` blocks for `calculate_BG_and_EQ` and `apply_BG_and_EQ` inside the `with ActionLogger(...)` block.

### Task 3: Add Method Definitions to `workflow` Class

**Files:**
- Modify: `Data_and_analysis/20260315_frames/workflow.py`

- [ ] **Step 1: Add `do_calculate_BG_and_EQ` method**
    Paste the definition after `do_calculate_equilization_map`.

- [ ] **Step 2: Add `do_apply_BG_and_EQ` method**
    Paste the definition after `do_calculate_BG_and_EQ`.

### Task 4: Validation

**Files:**
- Test: `Data_and_analysis/20260315_frames/workflow.py`

- [ ] **Step 1: Syntax check**
    Run `python3 -m py_compile Data_and_analysis/20260315_frames/workflow.py` to ensure no syntax errors.

- [ ] **Step 2: Verify `ActionLogger` handles new actions**
    (Optional/Manual) Check if `params_file.yml` needs corresponding sections for testing, but per user request, just ensure they "fit".

- [ ] **Step 3: Final Review**
    Ensure all imports are correct and there are no naming conflicts.
