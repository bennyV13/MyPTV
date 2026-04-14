# MyPTV Research Workstation Scaffolding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the existing MyPTV Web GUI into a modular, multi-page research workstation with categorized top navigation and a centralized action dispatcher.

**Architecture:** 
- **Frontend**: Registry-based navigation using a central `modules.ts` configuration to dynamically render top-bar dropdowns.
- **Backend**: Unified `POST /api/run_action` endpoint in FastAPI that dispatches commands to modular Python action handlers.
- **State**: Synchronized `params_file.yml` as the source of truth across all modules.

**Tech Stack:** React (TypeScript), Vite, FastAPI, Python 3.x.

**Protected Symbols:**
- `app` (FastAPI instance in `main.py`): Widely used, but modification is mandatory to implement the new dispatcher.
- `App` (React component in `App.tsx`): Will be refactored into a layout component.

**Regression Risks:**
- Refactoring `App.tsx` could temporarily break the "Initial Calibration" functionality until Phase 2 is complete.
- Changing API endpoints will require updating all existing frontend `apiCall` invocations.

---

### Task 0: Initialize Conductor Track Progress

**Files:**
- Modify: `conductor/tracks/web-gui/plan.md`

- [ ] **Step 1: Sync and File Plan**
Mark the "Implement Top Navigation with Categorized Dropdowns" task in `conductor/tracks/web-gui/plan.md` as IN PROGRESS.
Add a link to this plan: `[Implementation Plan: docs/superpowers/plans/2026-04-09-scaffolding.md](./docs/superpowers/plans/2026-04-09-scaffolding.md)` under Phase 1.

- [ ] **Step 2: Git Safety Gate**
Ensure a clean working directory. Commit current state if needed: `git add . && git commit -m "pre-scaffolding checkpoint"`.

---

### Task 1: Create Frontend Module Registry

**Files:**
- Create: `MyPTV/myptv/web_gui/frontend/src/modules.ts`
- Create: `MyPTV/myptv/web_gui/frontend/src/types.ts`

- [ ] **Step 1: Define types**
Create `types.ts` for the module registry structure.

```typescript
export interface Module {
  id: string;
  label: string;
  category: 'Preprocessing' | 'Calibration' | 'Processing' | 'Analysis' | 'System';
  component: React.LazyExoticComponent<any>;
}
```

- [ ] **Step 2: Create initial registry**
Set up `modules.ts` with a placeholder for the Initial Calibration module.

```typescript
import { lazy } from 'react';
import { Module } from './types';

export const modules: Module[] = [
  {
    id: 'initial_calibration',
    label: 'Initial Calibration',
    category: 'Calibration',
    component: lazy(() => import('./modules/calibration/InitialCalibration'))
  }
];
```

- [ ] **Step 3: Commit**
`git add MyPTV/myptv/web_gui/frontend/src/modules.ts MyPTV/myptv/web_gui/frontend/src/types.ts && git commit -m "feat: add frontend module registry"`

---

### Task 2: Implement Modular Layout and Top Navigation

**Files:**
- Modify: `MyPTV/myptv/web_gui/frontend/src/App.tsx`
- Create: `MyPTV/myptv/web_gui/frontend/src/components/Navigation.tsx`
- Create: `MyPTV/myptv/web_gui/frontend/src/components/Layout.tsx`

- [ ] **Step 1: Create Navigation component**
Implement a top-bar with dropdowns that group modules by category from the registry.

- [ ] **Step 2: Refactor App.tsx to Layout**
Move the main container, footer, and console logic into a `Layout` component. Use `<Suspense>` to load the active module's component.

- [ ] **Step 3: Implement Routing**
Use React state (`activeModuleId`) to switch between components in the main workspace.

- [ ] **Step 4: Commit**
`git commit -m "feat: implement modular layout and top navigation"`

---

### Task 3: Backend Action Dispatcher

**Files:**
- Modify: `MyPTV/myptv/web_gui/backend/main.py`
- Create: `MyPTV/myptv/web_gui/backend/actions/__init__.py`

- [ ] **Step 1: Define Action Request model**
Add a Pydantic model for action requests.

```python
class ActionRequest(BaseModel):
    action_id: str
    params: dict
```

- [ ] **Step 2: Implement /api/run_action**
Create the centralized dispatcher endpoint.

```python
@app.post("/api/run_action")
async def run_action(request: ActionRequest):
    # Mapping logic will go here
    return {"status": "dispatched", "action": request.action_id}
```

- [ ] **Step 3: Commit**
`git commit -m "feat: add backend action dispatcher endpoint"`

---

### Task Final: Finalize Conductor Track Progress

**Files:**
- Modify: `conductor/tracks/web-gui/plan.md`

- [ ] **Step 1: Sync Plan Completion**
Mark Phase 1 tasks as COMPLETED in `conductor/tracks/web-gui/plan.md`. Update progress to 20%.

- [ ] **Step 2: Final Impact Verification**
Run `git status` and verify clean build of the frontend.
