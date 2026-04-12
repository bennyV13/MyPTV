# Workstation Welcome Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a centralized Welcome Page with categorized action tiles as the default entry point for the MyPTV Workstation.

**Architecture:** Create a new `WelcomePage` component that renders a responsive grid of action tiles based on the `modules` registry. Update the `Layout` to default to this view.

**Tech Stack:** React (TypeScript), CSS Grid, Axios.

**Protected Symbols:** 
- `modules`: Widely used for navigation and rendering. (Modifying to add welcome page).
- `Layout`: Core application wrapper. (Modifying to set default state).

**Regression Risks:** 
- Incorrect module ID in `Layout` could break initial loading.
- CSS Grid conflicts with existing module styles.

---

### Task 0: Initialize Conductor Track Progress

**Files:**
- Modify: `conductor/tracks/web-gui-migration/plan.md`

- [ ] **Step 1: Sync and File Plan**
Mark "Implement Welcome Page" as IN PROGRESS and link this plan.
```markdown
- [/] Implement Welcome Page [Implementation Plan: docs/superpowers/plans/2026-04-12-workstation-welcome-page.md](../../docs/superpowers/plans/2026-04-12-workstation-welcome-page.md) <!-- IN PROGRESS -->
```

- [ ] **Step 2: Git Safety Gate**
`git add . && git commit -m "chore: pre-implementation checkpoint for welcome page"`

---

### Task 1: Create WelcomePage Component

**Files:**
- Create: `MyPTV/myptv/web_gui/frontend/src/modules/system/WelcomePage.tsx`

- [ ] **Step 1: Implement component**
Create the component with a grid of tiles based on categories.
```tsx
import React from 'react';
import { modules } from '../../modules';

interface WelcomePageProps {
  onModuleChange: (id: string) => void;
}

export default function WelcomePage({ onModuleChange }: WelcomePageProps) {
  const categories = ['Preprocessing', 'Calibration', 'Processing', 'Analysis', 'System'] as const;

  return (
    <div className="welcome-page">
      <header className="welcome-header">
        <h1>Welcome to MyPTV Workstation</h1>
        <p>Select a module to begin your analysis.</p>
      </header>
      
      <div className="action-grid">
        {categories.map(category => {
          const categoryModules = modules.filter(m => m.category === category && m.id !== 'welcome');
          if (categoryModules.length === 0) return null;

          return (
            <div key={category} className="category-tile" onClick={() => onModuleChange(categoryModules[0].id)}>
              <h2 className="category-title">{category}</h2>
              <ul className="action-list">
                {categoryModules.map(m => (
                  <li key={m.id}>
                    <button 
                      className="action-link" 
                      onClick={(e) => {
                        e.stopPropagation();
                        onModuleChange(m.id);
                      }}
                    >
                      {m.label}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Add styles to App.css**
```css
.welcome-page {
  padding: 3rem;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-header {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-header h1 {
  font-size: 2.5rem;
  color: #4facfe;
  margin-bottom: 0.5rem;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.category-tile {
  background-color: #2d2d2d;
  border: 1px solid #3e3e3e;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
}

.category-tile:hover {
  transform: translateY(-4px);
  border-color: #4facfe;
}

.category-title {
  font-size: 1.25rem;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #4facfe;
  border-bottom: 1px solid #3e3e3e;
  padding-bottom: 0.5rem;
}

.action-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.action-link {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  color: #cccccc;
  padding: 0.4rem 0;
  cursor: pointer;
  font-size: 0.95rem;
}

.action-link:hover {
  color: #ffffff;
  text-decoration: underline;
}
```

- [ ] **Step 3: Commit**
`git add MyPTV/myptv/web_gui/frontend/src/modules/system/WelcomePage.tsx MyPTV/myptv/web_gui/frontend/src/App.css`
`git commit -m "feat: implement WelcomePage component and styling"`

---

### Task 2: Register Welcome Module

**Files:**
- Modify: `MyPTV/myptv/web_gui/frontend/src/modules.ts`

- [ ] **Step 1: Add welcome module**
Add it at the beginning of the list.
```tsx
  // --- System ---
  {
    id: 'welcome',
    label: 'Welcome',
    category: 'System',
    component: lazy(() => import('./modules/system/WelcomePage'))
  },
```

- [ ] **Step 2: Commit**
`git commit -am "feat: register welcome module in workstation"`

---

### Task 3: Update Layout Default State

**Files:**
- Modify: `MyPTV/myptv/web_gui/frontend/src/components/Layout.tsx`

- [ ] **Step 1: Set default module to welcome**
Pass the `onModuleChange` prop to the `WelcomePage` component if it's the active one.
```tsx
export const Layout: React.FC<LayoutProps> = ({ logs, errorMsg }) => {
  const [activeModuleId, setActiveModuleId] = useState('welcome');
  // ...
  return (
    // ...
    <main className="workspace-main">
      <Suspense fallback={<div className="loading">Loading module...</div>}>
        {activeModuleId === 'welcome' ? (
          <ActiveComponent onModuleChange={setActiveModuleId} />
        ) : (
          <ActiveComponent />
        )}
      </Suspense>
    </main>
    // ...
  )
}
```

- [ ] **Step 2: Commit**
`git commit -am "feat: set welcome page as default workstation view"`

---

### Task 4: Rebuild and Verify

- [ ] **Step 1: Rebuild frontend**
`cd MyPTV/myptv/web_gui/frontend && npx vite build`

- [ ] **Step 2: Launch workstation**
`cd Data_and_analysis/Analysis/20260315_analysis && python workflow.py params_file.yml web_gui`

- [ ] **Step 3: Verify welcome page**
Confirm the dashboard is visible and navigation works.

---

### Task Final: Finalize Conductor Track Progress

**Files:**
- Modify: `conductor/tracks/web-gui-migration/plan.md`

- [ ] **Step 1: Mark Task as COMPLETED**
- [ ] **Step 2: Final Verification**
`git diff HEAD~4`
