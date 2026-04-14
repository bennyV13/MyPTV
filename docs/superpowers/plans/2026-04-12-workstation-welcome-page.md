# Workstation Welcome Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a centralized Welcome Page with categorized action tiles as the default entry point for the MyPTV Workstation, while removing broken navigation and ensuring Python is the source of truth.

**Architecture:** Create a new `WelcomePage` component. Refactor `Layout.tsx` to remove the old `Navigation` bar and add a simple "Home" button. Fetch configuration from the backend to ensure the UI reflects the `params_file.yml`.

**Tech Stack:** React (TypeScript), CSS Grid, Axios.

**Protected Symbols:** 
- `modules`: Widely used for navigation and rendering.
- `Layout`: Core application wrapper.

**Regression Risks:** 
- Broken "Home" button could trap users in a module.
- Inconsistent config display if backend synchronization fails.

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
`git add . && git commit -m "chore: pre-implementation checkpoint for welcome page refinements"`

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
        <h1>MyPTV Workstation</h1>
        <p>Python-driven PTV analysis. Params file is the source of truth.</p>
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

.home-button {
  background: #3e3e3e;
  border: 1px solid #555;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 1rem;
  font-size: 0.8rem;
}

.home-button:hover {
  background: #4facfe;
  color: black;
}
```

- [ ] **Step 3: Commit**
`git add MyPTV/myptv/web_gui/frontend/src/modules/system/WelcomePage.tsx MyPTV/myptv/web_gui/frontend/src/App.css`
`git commit -m "feat: implement WelcomePage component and styling"`

---

### Task 2: Refactor Layout and Navigation

**Files:**
- Modify: `MyPTV/myptv/web_gui/frontend/src/components/Layout.tsx`
- Delete: `MyPTV/myptv/web_gui/frontend/src/components/Navigation.tsx`

- [ ] **Step 1: Remove Navigation and add Home button**
Refactor the header to remove the broken navigation and add a simple "Home" button that returns to the welcome page. Also, make the footer configuration dynamic by fetching it from `/api/config`.

```tsx
import React, { Suspense, useState, useEffect } from 'react';
import axios from 'axios';
import { modules } from '../modules';

interface LayoutProps {
  logs: string[];
  errorMsg: string | null;
}

export const Layout: React.FC<LayoutProps> = ({ logs, errorMsg }) => {
  const [activeModuleId, setActiveModuleId] = useState('welcome');
  const [isConsoleOpen, setIsConsoleOpen] = useState(true);
  const [config, setConfig] = useState<any>(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await axios.get('/api/config');
        setConfig(res.data);
      } catch (e) {}
    };
    fetchConfig();
  }, [activeModuleId]);

  const activeModule = modules.find(m => m.id === activeModuleId) || modules[0];
  const ActiveComponent = activeModule.component;

  return (
    <div className="workstation-layout">
      <header className="top-nav">
        <div className="nav-logo">MyPTV Workstation</div>
        <div className="nav-actions">
          {activeModuleId !== 'welcome' && (
            <button className="home-button" onClick={() => setActiveModuleId('welcome')}>
              ← Back to Dashboard
            </button>
          )}
        </div>
        <div className="nav-status">
          <span className="status-indicator online"></span> Server: Online
        </div>
      </header>
      
      <main className="workspace-main">
        <Suspense fallback={<div className="loading">Loading module...</div>}>
          {activeModuleId === 'welcome' ? (
            <ActiveComponent onModuleChange={setActiveModuleId} />
          ) : (
            <ActiveComponent />
          )}
        </Suspense>
      </main>

      <footer className={`workstation-footer ${isConsoleOpen ? 'console-open' : ''}`}>
        <div className="footer-status-bar">
          <div className="status-left">
            <span>Params: {config?.calibration?.camera_name || 'Not set'}</span>
            <span className="separator">|</span>
            <span>Image: {config?.calibration?.calibration_image || 'None'}</span>
          </div>
          <button className="console-toggle" onClick={() => setIsConsoleOpen(!isConsoleOpen)}>
            {isConsoleOpen ? 'Collapse Console ▾' : 'Open Console ▴'}
          </button>
        </div>
        {/* ... console drawer ... */}
      </footer>
      {/* ... error banner ... */}
    </div>
  );
};
```

- [ ] **Step 2: Delete Navigation.tsx**
`rm MyPTV/myptv/web_gui/frontend/src/components/Navigation.tsx`

- [ ] **Step 3: Register welcome module in modules.ts**
Add `id: 'welcome'` at the beginning.

- [ ] **Step 4: Commit**
`git commit -am "feat: refactor layout to remove broken navigation and add home button"`

---

### Task 3: Rebuild and Verify

- [ ] **Step 1: Rebuild frontend**
`cd MyPTV/myptv/web_gui/frontend && npx vite build`

- [ ] **Step 2: Verify "Python is the brain"**
Ensure that changes in `params_file.yml` (reflected in the backend) appear in the footer.

- [ ] **Step 3: Verify navigation**
Confirm that clicking "Back to Dashboard" always returns to the welcome page.

---

### Task Final: Finalize Conductor Track Progress

**Files:**
- Modify: `conductor/tracks/web-gui-migration/plan.md`

- [ ] **Step 1: Mark Task as COMPLETED**
- [ ] **Step 2: Final Verification**
`git diff HEAD~4`
