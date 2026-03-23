# Lagrangian Analysis: Review & Improvement Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Register the Lagrangian analysis project in Conductor and perform a deep technical review of the statistical computation logic (`calculate_stats.py`) to identify areas for accuracy and performance improvements.

**Architecture:** Use the Conductor framework to track progress and document findings. The review phase will involve code analysis and documentation of the current `calculate_stats.py` implementation.

**Tech Stack:** Conductor (Markdown), Python (Lagrangian scripts).

---

### Task 1: Register Track in Conductor

**Files:**
- Modify: `conductor/tracks.md`
- Create: `conductor/tracks/lagrangian-analysis/index.md`
- Create: `conductor/tracks/lagrangian-analysis/metadata.json`

- [ ] **Step 1: Add track to registry**

Update `conductor/tracks.md` to include the `lagrangian-analysis` entry.

- [ ] **Step 2: Create track folder and index**

Create `conductor/tracks/lagrangian-analysis/index.md` with the following content:
```markdown
# Track: Lagrangian Data Analysis

## Goal
Review and improve the Lagrangian analysis pipeline, focusing on statistical accuracy and efficiency.

## Workflow Checklist
- [ ] Ingest PTV Data (`traj2npy.py`)
- [ ] Spatial Partitioning (`divide_points_to_cube_voxels.py`)
- [ ] **Deep Review: Statistical Computation (`calculate_stats.py`)**
- [ ] Refine Results (`remove_zero_vox.py`)
- [ ] Visualization (`plot_lagrangian_results.py`)
```

- [ ] **Step 3: Create metadata.json**

Create `conductor/tracks/lagrangian-analysis/metadata.json`:
```json
{
  "id": "lagrangian-analysis",
  "name": "Lagrangian Data Analysis Pipeline",
  "status": "active",
  "path": "conductor/tracks/lagrangian-analysis/"
}
```

- [ ] **Step 4: Commit registry and initial track files**

```bash
git add conductor/tracks.md conductor/tracks/lagrangian-analysis/
git commit -m "feat(conductor): register lagrangian-analysis track"
```

### Task 2: Deep Review of `calculate_stats.py`

**Files:**
- Read: `analyzing_softwares_copy/analyzing_softwares/velocity_field_lagrangian/calculate_stats.py`
- Read: `analyzing_softwares_copy/analyzing_softwares/velocity_field_lagrangian/voxel_class.py`
- Create: `conductor/tracks/lagrangian-analysis/step3_review.md`

- [ ] **Step 1: Analyze statistical methods**

Read `calculate_stats.py` and `voxel_class.py` to identify how means, fluctuations, and spatial derivatives are calculated.

- [ ] **Step 2: Document current implementation**

Create `conductor/tracks/lagrangian-analysis/step3_review.md` documenting:
- The multi-phase pipeline (Stats 1, 2, 3).
- Mathematical formulas used for turbulence metrics.
- Known constraints or performance bottlenecks.

- [ ] **Step 3: Propose improvements**

Add a "Proposed Improvements" section to `step3_review.md` based on the code review (e.g., vectorization opportunities, error handling, or new physical metrics).

- [ ] **Step 4: Commit review findings**

```bash
git add conductor/tracks/lagrangian-analysis/step3_review.md
git commit -m "docs(lagrangian): complete initial review of calculate_stats.py"
```
