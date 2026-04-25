# Project Overview

## Purpose

Build a **pixel-accurate mock of Figma Design** (the application) with a
well-defined subset of core editing functionality and a comprehensive
**action logger** that captures both raw input events and semantic
user-intent events.

The mock is the editor-facing component of a larger CUA (Computer Use
Agent) testing system. Upstream pieces (CUA model, adapter, bridge) and
downstream pieces (test harness, trajectory assertions) are not part of
this project's output — only the Mock App + its logger.

---

## What we have

### 1. Figma documentation corpus — `helper/figma_docs/`

- **216 articles** scraped from Figma's help center
- Covers four products: Figma Design (175), Dev Mode (19), Projects (19), Figma Draw (3)
- Each article: `content.md` (full markdown) + `metadata.json` (URL, breadcrumb, internal links, images)
- Also: `index.json` (all articles with IDs, titles, products), `graph.json` (link graph: 216 nodes, 1,046 edges, 468 external references)

### 2. Synthesized analysis — `helper/analysis/`

Five curated documents distilled from the 216 articles:

- **`ui-map.md`** (19KB) — UI3 spatial layout: toolbar (bottom-center), left navigation panel, right properties panel, canvas. Mode variants (Dev Mode, Draw mode, view-only).
- **`panel-states.md`** (41KB) — Every panel documented with location, show-when, contents, change-when.
- **`feature-inventory.md`** (186KB) — Exhaustive flat list of every feature. Per feature: domain, UI location, trigger, inputs, outputs, related features, source article.
- **`workflows.md`** (54KB) — Multi-step user flows (masks, bulk rename, auto-layout, vector networks, etc.).
- **`dependency-clusters.md`** (13KB) — Graph analysis: hub articles by in/out-degree, cross-product edges, and a suggested tier structure derived from the graph.

Plus `_partial/` — raw per-domain extracts (gitignored; deeper detail when the synthesized files are ambiguous).

### 3. OpenPencil reference — `open-source-example/open-pencil/`

- Open-source Figma-compatible editor (MIT license, ~147MB shallow clone)
- Stack: Vue 3 + TypeScript + Vite + canvaskit-wasm (Skia) + yoga-layout + Yjs + Tauri
- Monorepo: `packages/core` (framework-agnostic), `packages/vue` (Vue input layer), `packages/cli`, `packages/mcp`, `packages/docs`
- Useful patterns to study: nanoevents emitter in `SceneGraph`, inverse-op undo closures, Figma-HTML clipboard format, hit-testing with nested scoping, snap-guides
- Vue UI layer, Tauri shell, AI/MCP code, `.fig` binary parser are present but not relevant to our problem

---

## What we can do with what we have

| Need | Source |
|------|--------|
| "Does Figma have feature X?" | `analysis/feature-inventory.md` |
| "What does panel Y show when Z is selected?" | `analysis/panel-states.md` |
| "What's the multi-step flow for doing X?" | `analysis/workflows.md` |
| "What's foundational / where do features sit in the dependency order?" | `analysis/dependency-clusters.md` |
| "Where does panel / toolbar sit on the screen?" | `analysis/ui-map.md` |
| "How is SceneGraph-like data shaped in an existing editor?" | `open-pencil/packages/core/src/scene-graph/` |
| "How does an inverse-op undo look?" | `open-pencil/packages/core/src/editor/undo.ts` |
| "How does drag-move commit work?" | `open-pencil/packages/vue/src/shared/input/move.ts` |
| "How is copy/paste made Figma-compatible?" | `open-pencil/packages/core/src/editor/clipboard.ts` |
| "Full article context for a specific feature" | `helper/figma_docs/articles/<Product>/<slug>/content.md` |

What these materials **do not** directly give us:
- Exact-to-the-pixel spacings, font metrics, colors of specific UI elements
- Hover / focus / transition animations
- Figma's proprietary icon set
- Inter font metrics at each weight
- Any runtime behavior of actual Figma that isn't described in the articles

These gaps require either screenshots, DevTools inspection on the real Figma, or substitution with open equivalents (Google Fonts, Lucide icons, etc.).

---

## What we need to decide

None of the items below are decided. They are listed so we can see the surface of the decision space.

### Scope
- Which features from `feature-inventory.md` are in the build and which are out
- Which Figma modes are supported (Design alone, Design + Draw, more)
- Whether the design-system layer (components, variants, variables) is in scope

### Technical
- Frontend framework
- State management library and store shape
- Canvas rendering approach (Canvas 2D, SVG, WebGL, canvaskit-wasm)
- CSS / styling approach
- Build tool and TypeScript config
- Project / directory layout
- Font and icon strategy
- Whether to reuse any OpenPencil code or only read it as reference

### Logger
- The semantic event taxonomy — what semantic events we emit
- Where in the code each semantic event fires (the emission points)
- Log schema fields and storage format
- Which raw browser events to capture and at which DOM level
- Where logs persist and how they are exported

### Process
- Build order — UI first, engine first, thin vertical slice, or other
- How screenshots and other visual references are added and consumed
- How each step is reviewed and signed off
- Whether one-shot agent delegation or step-by-step human-directed work is the working mode

### Architectural forward-compatibility
- Whether the UI shell is designed for future mode swaps (Dev Mode, Prototype mode, etc.)
- Whether the data model anticipates future extensions (components, variables, collaboration)
- Whether the event taxonomy is a registry or a closed set
- Whether the log schema is versioned
