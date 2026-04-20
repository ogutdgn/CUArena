# Phase 4 — Implementation

## Your Role

You are a frontend developer. Build the CUA mock application based on the
Phase 3 architecture documents.

## Context

You are building a mock Figma Design interface for CUA (Computer Use Agent)
testing. The CUA will see this app's screen and interact with it.

## Objectives

1. Build the UI shell (toolbar, sidebars, canvas placeholder, menus)
2. Implement the state machine (actions trigger state transitions)
3. Wire up keyboard shortcuts
4. Pre-populate mock data (layers, frames, components)
5. Implement the selected workflows from Phase 2
6. Add visual feedback for every state change

## Input Files

Read Phase 3 outputs (in `architecture/` directory):
- `tech-stack.md` — what to build with
- `state-machine.md` — states and transitions to implement
- `component-tree.md` — UI component structure
- `data-model.md` — TypeScript interfaces
- `test-scenarios.md` — what the app must support

Also reference the original documentation when you need UI details:
- `figma_docs/articles/<slug>/content.md` — exact button labels, menu items, panel sections
- `figma_docs/articles/<slug>/images/` — screenshots of the real Figma UI

## Implementation Rules

1. **Match Figma's labels exactly** — Button text, menu items, panel headers
   must use the same words as real Figma. CUA relies on text recognition.

2. **Use semantic HTML** — Buttons must be `<button>`, links must be `<a>`,
   inputs must be `<input>`. CUA uses accessibility tree for element detection.

3. **Consistent layout** — Toolbar at top, layers panel on left, properties
   on right, canvas in center. Match the spatial layout from "Navigating UI3" article.

4. **State indicators must be visible** — When auto layout is active, show
   the auto layout panel. When a component is selected, show component properties.
   CUA verifies actions by checking visual state.

5. **No loading states or async** — Everything must be instant. CUA cannot
   wait for animations or loading spinners.

## Build Order

1. Static UI shell (all panels visible, no interactivity)
2. Layer tree with selection (click layer → properties panel updates)
3. Toolbar actions (create frame, add text, add shape)
4. Right sidebar interactions (change properties, add auto layout)
5. Keyboard shortcuts
6. Workflow-specific features from Phase 2 scope
7. Test scenarios validation

## Output

The mock app source code, buildable and runnable locally.
