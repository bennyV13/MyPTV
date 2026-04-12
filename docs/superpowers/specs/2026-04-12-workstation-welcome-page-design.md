# Design Spec: MyPTV Workstation Welcome Page

**Date:** 2026-04-12  
**Status:** Approved  
**Track:** [Web GUI Migration](../../conductor/tracks/web-gui-migration/index.md)

## Overview
The goal is to implement a "Welcome Page" for the MyPTV Workstation that serves as an intuitive entry point for users. Instead of defaulting to a specific module (like Initial Calibration), the app will present a high-level dashboard where users can choose from categorized "bins" of functionality.

## Requirements
- **Unified Entry Point:** The welcome page must be the default view when the application launches.
- **Action Dashboard:** A clean, responsive grid layout featuring tiles for each major action category.
- **Categorized Actions:** Each tile must display its category name and a comprehensive list of all actions available within that bin.
- **Direct Navigation:** Clicking a tile or an action link must navigate the user directly to the corresponding workstation module.
- **Consistent Styling:** The design must align with the existing dark-themed workstation layout and use the "MyPTV Workstation" branding.

## Architecture & Components

### 1. WelcomePage Component (`src/modules/system/WelcomePage.tsx`)
- **Grid Layout:** A CSS grid container for the action tiles.
- **ActionTile Component:** A sub-component that renders an individual tile with its category and action list.
- **State Management:** Uses the `onModuleChange` callback from the parent `Layout` component to switch views.

### 2. Layout Integration (`src/components/Layout.tsx`)
- **Default State:** Update the `activeModuleId` default state to `'welcome'`.
- **Module Registration:** Register the `WelcomePage` in `src/modules.ts`.

## Bins & Actions Mapping
The following mapping will be used to populate the dashboard:

| Category | Actions |
|---|---|
| **Preprocessing** | Segmentation, Calculate BG Image, Calculate EQ Map, Calculate BG & EQ, Create Blob Mask |
| **Calibration** | Initial Calibration, Final Calibration, Analyze Error, Calibration with Particles, Legacy Calibration, Legacy Point GUI, Match Target File |
| **Processing** | Matching, Manual Matching, 2D Tracking, Tracking, Stitching, Smoothing |
| **Analysis** | Analyze Disparity, Plot Trajectories, Animate Trajectories, Fiber Orientations |
| **System** | Operation Log, Run Extension |

## Visual Design
- **Background:** `#1e1e1e` (Existing workstation background).
- **Tiles:** `#2d2d2d` with subtle borders and hover effects.
- **Typography:** Consistent with the workstation's sans-serif stack.
- **Logo:** "MyPTV Workstation" prominently displayed in the navigation bar.

## Verification Plan
- **Manual Test:** Launch the web GUI and verify the welcome page is the default view.
- **Navigation Test:** Click on each tile and action link to ensure it navigates to the correct module.
- **Layout Test:** Verify the grid is responsive and renders correctly on different screen sizes.
- **Styling Test:** Ensure no styling conflicts with existing modules.
