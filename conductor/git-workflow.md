# Git Strategy Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a standard feature branch and integration workflow for the MyPTV project.

**Architecture:** Create independent feature branches from `master` for clean Pull Requests, and merge them into `gemini-changes` for combined local testing.

**Tech Stack:** Git

---

### Task 1: Prepare the Base Environment

**Files:**
- none

- [ ] **Step 1: Save current work on gemini-changes**
Run: `git checkout gemini-changes && git add . && git commit -m "chore: save local progress before branching"`
Expected: Commit successful or nothing to commit.

- [ ] **Step 2: Update master branch**
Run: `git checkout master && git pull origin master`
Expected: `master` is up to date with the remote clean state.

---

### Task 2: Create a New Feature Branch

**Files:**
- none

- [ ] **Step 1: Branch from clean master**
Run: `git checkout master && git checkout -b feature/<feature-name>`
Expected: Switched to a new branch `feature/<feature-name>`.

- [ ] **Step 2: Implement feature changes**
(Develop, test, and commit the isolated changes here.)

---

### Task 3: Combine with Local Changes (Integration)

**Files:**
- none

- [ ] **Step 1: Switch to local integration branch**
Run: `git checkout gemini-changes`

- [ ] **Step 2: Merge the new feature**
Run: `git merge feature/<feature-name>`
Expected: The new feature is successfully merged. Resolve any conflicts if they arise.

---

### Task 4: Push Feature for Upstream PR

**Files:**
- none

- [ ] **Step 1: Push the isolated feature branch**
Run: `git push origin feature/<feature-name>`
Expected: Branch pushed successfully. You can now open a PR from this branch to `upstream/master`.
