# React Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Jinja/static-JS visualization frontend with a React single-page application while keeping the existing Flask JSON APIs, MySQL access, crawler, and data-cleaning pipeline intact.

**Architecture:** The React app lives in `frontend/` and uses Vite, React Router, TypeScript, and ECharts. Flask continues to expose `/api/*` and serves the compiled React app for page routes when `frontend/dist/index.html` exists, while preserving existing template fallback for local Python-only smoke tests.

**Tech Stack:** Python 3.11, Flask, Pytest, Node 22, Vite, React, TypeScript, Vitest, React Testing Library, ECharts.

---

## File Structure

- Create `frontend/package.json`: npm scripts and dependencies.
- Create `frontend/vite.config.ts`: Vite React config and `/api` proxy.
- Create `frontend/tsconfig*.json`: TypeScript compiler config.
- Create `frontend/index.html`: React SPA entry document.
- Create `frontend/src/api/types.ts`: API payload contracts matching Flask responses.
- Create `frontend/src/api/weatherApi.ts`: typed `fetch` wrapper for `/api/*`.
- Create `frontend/src/components/*`: reusable cards, chart panel, ECharts wrapper, search, and table components.
- Create `frontend/src/pages/*`: Dashboard, map, analysis, and history pages.
- Create `frontend/src/layouts/AppLayout.tsx`: sidebar and content shell.
- Create `frontend/src/App.tsx` and `frontend/src/main.tsx`: route setup and app bootstrap.
- Create `frontend/src/styles/global.css`: migrated and refined dashboard styles.
- Create `frontend/public/vendor/china.js`: copy of the existing ECharts China map registration script.
- Modify `app/routes/pages.py`: serve React build when available.
- Modify `tests/test_routes.py`: keep API coverage and accept React-build fallback behavior.

## Task 1: Frontend Scaffold

- [ ] Create Vite React TypeScript package files.
- [ ] Install npm dependencies and generate `package-lock.json`.
- [ ] Add Vitest setup and a smoke test that initially fails because `App` is missing.
- [ ] Implement the minimum app shell so the smoke test passes.

## Task 2: API Layer

- [ ] Add TypeScript payload interfaces for dashboard, map, analysis, and history data.
- [ ] Add API client tests using a stubbed `fetch`.
- [ ] Implement `weatherApi.ts` with error handling for non-OK responses.
- [ ] Run frontend tests.

## Task 3: React Pages and Components

- [ ] Add reusable layout, stat card, chart panel, ECharts, history table, and city search components.
- [ ] Implement four pages mapped to `/`, `/map`, `/analysis`, and `/history`.
- [ ] Use existing `/api/*` endpoints as the only data source.
- [ ] Include loading and empty states for every page.

## Task 4: Flask Integration

- [ ] Add route tests for React build serving behavior.
- [ ] Update `pages.py` to return `frontend/dist/index.html` when present.
- [ ] Preserve current template rendering when no React build exists.
- [ ] Run Python route tests.

## Task 5: Verification

- [ ] Run `npm test -- --run`.
- [ ] Run `npm run build`.
- [ ] Run `python -m pytest -v`.
- [ ] Review `git diff` for accidental unrelated changes.
