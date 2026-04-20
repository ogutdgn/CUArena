# Phase 3 — Architecture

## Your Role

You are a software architect. Design the technical architecture for the CUA
mock application based on the Phase 2 scope decisions.

## Context

This is a mock Figma for CUA testing. Key constraints:
- CUA interacts via screen pixels — the app must render real HTML elements
- No real canvas rendering needed — state simulation is sufficient
- Must be deterministic — same input = same visual output
- Must be web-based — CUA operates on browser screenshots

## Objectives

1. **Tech Stack Selection** — Choose the right tools for a mock UI app.
   Consider: Next.js, plain React, or even vanilla HTML/CSS/JS.
   The simpler the better — this is a mock, not a product.

2. **State Machine Design** — Define the app's state model:
   - What states exist (empty canvas, layer selected, auto layout active, etc.)
   - What transitions are possible (user actions)
   - What UI changes per state (which panels show what)

3. **Component Architecture** — Map Figma's UI to web components:
   - Toolbar component
   - Left sidebar (layers panel)
   - Right sidebar (properties panel)
   - Canvas area (simplified)
   - Menus and modals

4. **Mock Data Model** — Define the data structures:
   - Layer/frame/component objects
   - Properties (position, size, fills, effects, etc.)
   - Pre-populated mock data for testing scenarios

## Input Files

Read Phase 2 outputs (in `scope/` directory):
- `tier-classification.md` — what features are in scope
- `selected-workflows.md` — what workflows to support
- `fidelity-matrix.md` — how real each feature needs to be
- `mock-ui-spec.md` — UI requirements

## Design Principles

1. **State over rendering** — Don't render shapes. Change panel content and
   layer tree state. CUA tests actions and UI feedback, not pixel rendering.

2. **Convention over configuration** — Hardcode mock data. Don't build a
   generic design tool engine. Build exactly what the test scenarios need.

3. **Visible feedback for every action** — CUA needs to verify its actions
   succeeded. Every user action must produce a visible UI change.

4. **Keyboard shortcuts must work** — CUA uses both click and keyboard.
   Implement the shortcuts from the documentation.

## Output Format

Save architecture to `architecture/` directory:
- `architecture/tech-stack.md` — chosen technologies and rationale
- `architecture/state-machine.md` — states, transitions, diagram
- `architecture/component-tree.md` — UI component hierarchy
- `architecture/data-model.md` — TypeScript interfaces for mock data
- `architecture/test-scenarios.md` — pre-defined CUA test scenarios with expected states
