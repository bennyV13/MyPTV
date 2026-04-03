# Universal Plotting Style Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the `LagrangianAnalysis` class to use a centralized `_apply_style` method for all plotting, ensuring visual consistency and reducing code duplication.

**Architecture:** Implement a private `_apply_style` helper method that handles all boilerplate (titles, labels, grids, legends, saving, showing) and refactor existing plot methods (`plot_msd`, `plot_pdf`, `plot_lvacf`) to use it.

**Tech Stack:** `matplotlib`, `numpy`, `python`

**Protected Symbols:** `LagrangianAnalysis` (widely used in research notebooks and analysis scripts).

**Regression Risks:** Modification of plot method signatures (though we will maintain parameter names) or changes to default visual appearances that might affect existing report layouts.

---

### Task 0: Initialize Conductor Track Progress

**Files:**
- Modify: `conductor/tracks/lagrangian-analysis/index.md`

- [ ] **Step 1: Sync and File Plan**
Mark "Phase 4: Export & Visualization -> Step 9: Plotting" as IN PROGRESS (or update status if already complete to reflect refinement). 
Add a link to this current plan (`[Implementation Plan: docs/superpowers/plans/2026-03-15-universal-plotting-style.md](docs/superpowers/plans/2026-03-15-universal-plotting-style.md)`) directly under Step 9.

- [ ] **Step 2: Git Safety Gate**
Ensure a clean working directory.
Run: `git status`
Expected: No unstaged changes.

---

### Task 1: Implement `_apply_style` Helper

**Files:**
- Modify: `Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py`

- [ ] **Step 1: Add the helper method**
Add `_apply_style` to the class.

```python
    def _apply_style(self, ax, title, xlabel, ylabel, save_path=None, logx=False, logy=False):
        """
        Applies consistent styling to a Lagrangian plot.
        """
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        
        if logx: ax.set_xscale('log')
        if logy: ax.set_yscale('log')
        
        ax.grid(True, which="both", ls="-", alpha=0.3)
        ax.legend(frameon=True, shadow=True)
        
        # Modern look: hide top/right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        plt.show()
```

- [ ] **Step 2: Commit**
Run: `git add Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py && git commit -m "feat: add _apply_style helper to LagrangianAnalysis"`

---

### Task 2: Refactor `plot_msd`

**Files:**
- Modify: `Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py`

- [ ] **Step 1: Update `plot_msd`**
Replace the boilerplate with the new helper.

```python
    def plot_msd(self, save_path=None):
        """Plot the calculated MSD."""
        if 'msd' not in self.results:
            print("MSD not calculated.")
            return
            
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(self.results['msd_lags'], self.results['msd'], 'o-', 
                label='Data', color='#1f77b4', markersize=4)
        
        self._apply_style(ax, 
                          title='Mean Squared Displacement (Taylor 1921)',
                          xlabel='Time lag [frames]',
                          ylabel='MSD [length units$^2$]',
                          save_path=save_path, 
                          logx=True, logy=True)
```

- [ ] **Step 2: Commit**
Run: `git add Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py && git commit -m "refactor: use _apply_style in plot_msd"`

---

### Task 3: Refactor `plot_pdf`

**Files:**
- Modify: `Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py`

- [ ] **Step 1: Update `plot_pdf`**
Replace the boilerplate with the new helper.

```python
    def plot_pdf(self, kind='vx', save_path=None):
        """Plot the calculated PDF."""
        key = f'pdf_{kind}'
        if key not in self.results:
            print(f"PDF for {kind} not calculated.")
            return
            
        centers, hist = self.results[key]
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(centers, hist, 'o-', label=f'Data {kind}', 
                color='#1f77b4', markersize=4)
        
        self._apply_style(ax, 
                          title=f'Probability Density Function: {kind}',
                          xlabel=f'{kind} [units]',
                          ylabel='PDF',
                          save_path=save_path, 
                          logy=True)
```

- [ ] **Step 2: Commit**
Run: `git add Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py && git commit -m "refactor: use _apply_style in plot_pdf"`

---

### Task 4: Refactor `plot_lvacf`

**Files:**
- Modify: `Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py`

- [ ] **Step 1: Update `plot_lvacf`**
Replace the boilerplate with the new helper.

```python
    def plot_lvacf(self, kind='vx', save_path=None):
        """Plot the calculated LVACF."""
        key = f'lvacf_{kind}'
        if key not in self.results:
            print(f"LVACF for {kind} not calculated.")
            return
            
        lvacf = self.results[key]
        lags = self.results[f'lvacf_lags_{kind}']
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(lags, lvacf, 'o-', label=f'Data {kind}', 
                color='#1f77b4', markersize=4)
        ax.axhline(0, color='k', linestyle='--', alpha=0.3)
        
        self._apply_style(ax, 
                          title=f'Lagrangian Velocity Autocorrelation Function: {kind}',
                          xlabel='Time lag [frames]',
                          ylabel='$R_L(\\tau)$',
                          save_path=save_path)
```

- [ ] **Step 2: Commit**
Run: `git add Data_and_analysis/Analysis/analyzing_softwares/lagrangian_analysis_suite/lagrangian_analysis.py && git commit -m "refactor: use _apply_style in plot_lvacf"`

---

### Task Final: Finalize Conductor Track Progress

**Files:**
- Modify: `conductor/tracks/lagrangian-analysis/index.md`

- [ ] **Step 1: Sync Plan Completion**
Mark Step 9 as COMPLETED and add a note about the standardized plotting style.

- [ ] **Step 2: Final Impact Verification**
Run `git diff HEAD~5` to review all changes. Verify that the `LagrangianAnalysis` class logic is intact and only visual presentation code was consolidated. Verify no imports were broken.
