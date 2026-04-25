# Plan 00 — Overview

## 1. Purpose

Single entry point for the project's build strategy. Reading this document + the other four `plan/*.md` files should be enough for a new contributor (human or agent) to understand *what* we are building, *how* we plan to build it, and *why* this particular order.

## 2. What we are building

- **A pixel-accurate mock of Figma Design** (the application), scoped to Tier 2 of the feature tiering discussed in conversation.
- **An action logger** that captures:
  - Raw browser input events (mouse, keyboard, pointer)
  - Semantic user-intent events (e.g., `drag_move`, `copy`, `paste`, `create_rectangle`)
- Output is consumable by a downstream CUA (Computer Use Agent) test harness. Trajectories — not just final state — must be distinguishable from the log (e.g., "object moved via drag" vs "object moved via copy+paste").

### Two kinds of scope — do not conflate

This project has two distinct scopes that must be tracked separately:

- **Functional scope** — features whose *behavior* we implement. Clicking the tool does something. The engine supports it. The logger emits semantic events for it.
- **Visual (UI) scope** — UI elements whose *appearance* we render. Buttons, tabs, menu items, mode toggles. These are visible on the screen even if their behavior is not implemented.

**Visual scope is a strict superset of functional scope.**

The real Figma toolbar, sidebars, and chrome contain many buttons for features that are out of our functional scope (e.g., the Draw mode toggle, the Dev Mode button, the Prototype tab, the Auto layout button, the Components sub-header action). These UI elements **must all be rendered**, with correct position, size, icon, and default appearance, even though clicking them does nothing meaningful. Without them, the mock does not look like Figma.

See §3 for exactly what is functional-scope only vs fully out.

**Tier 2 functional scope (decided):**

- All shape tools: rectangle, line, arrow, ellipse, polygon, star
- Image / video import and display
- Frame, section, slice
- Move / hand / scale tools
- Selection + multi-selection (click, shift-click, drag-box)
- Copy / paste / drag-drop / delete
- Pen tool + vector network + vector edit mode
- Pencil tool (stroke → vector)
- Full text editing (caret, selection, wrapping, font weight / size / color)
- Effects (drop shadow, blur)
- Constraints
- Pages (multi-page)
- Layers panel (left sidebar) with hierarchy, rename, reorder, delete
- Right sidebar with Position, Size, Fill, Stroke, Effects
- Groups, parent / child relationships
- Undo / redo
- Canvas pan / zoom, snap / smart guides

## 3. Out of functional scope (UI still rendered)

These features are **not** implemented behaviorally — but the UI elements that represent them in real Figma **are** still rendered, with the correct visual appearance and position. Clicking them is a no-op (or at most shows a brief "not implemented" indicator; exact behavior TBD in `plan/03`). Their presence on screen is required for UI fidelity.

- **Dev Mode** — mode switcher button visible in toolbar; switching to Dev Mode UI is not implemented
- **Figma Draw** — Draw toggle button visible in toolbar; switching to Draw mode is not implemented
- **Prototype tab** — tab visible in right sidebar header; tab content not rendered (click does nothing or shows empty state)
- **Design system layer** — sub-header buttons (Create component, Mask, Boolean ops icons), Assets tab entry, Variables modal entry, Component properties sections: all visible where applicable, non-functional
- **Auto layout** — "Use auto layout" button visible in Layout section of right sidebar; non-functional
- **Boolean operations** — sub-header button visible when 2+ shapes selected; non-functional
- **Comments / multiplayer** — Comment tool visible in toolbar; avatar stack / Share button visible in top chrome; Comment mode not enterable
- **Annotations / Measurements** (Dev Mode tools) — visible in toolbar under Comment dropdown; non-functional
- **Actions menu** — sparkle icon visible in toolbar; clicking does not open the menu (or opens an empty placeholder)
- **Rulers, guides, pixel grid, layout guides** — menu options visible in Zoom / view dropdown; non-functional
- **Styles as reusable primitives** — "Apply style" swatch slots visible in Fill / Stroke / Effects sections; clicking does not open the style picker
- **Libraries** — Libraries modal entry button visible; non-functional
- **Branching / version history / share** — entries visible in file-name dropdown menu; non-functional
- **AI features** — any sparkle-branded entry visible; non-functional
- **Import / export beyond image drop** — Export section visible when something is selected; clicking Export does nothing (or downloads a stub, TBD)
- **RTL / CJK / advanced text features** — any text property that targets them is not behaviorally implemented, but the corresponding right-sidebar control is still rendered if it appears in the default UI

### 3a. Fully out — not rendered at all

Things that are *not* part of default Figma Design chrome and should not appear anywhere:

- Dev Mode-only overlays (annotation dots, measurement nodes, status badges) — only appear when user is in Dev Mode, which we don't enter
- Prototype noodles, flow start badges — only appear in Prototype mode, which we don't enter
- Draw mode secondary toolbars (brush/pencil style pickers) — only appear in Draw mode, which we don't enter
- FigJam, Figma Buzz, Figma Slides UI — different product surfaces entirely
- View-only / Dev-seat chrome variants — we always render the edit-access view

### 3b. Scope guardrails

- Any feature that drifts *functionally* out of §2 is recorded as an open question rather than silently implemented.
- Any UI element from §3 that turns out to need minimal behavior to look correct (e.g., a dropdown whose *arrow rotates* but whose menu doesn't open) gets flagged for user decision.
- No-op clicks on §3 elements: logger behavior for these is an open question — see `plan/03`.

## 4. Guiding principles

1. **UI fidelity is driven by the docs corpus**, not guesswork. Every UI element's look + states must trace back to an article image or explicit spec in `helper/figma_docs` / `helper/analysis`. When the corpus doesn't cover a state, the gap is flagged and a screenshot is requested rather than invented.
2. **UI completeness.** The rendered UI reflects the full real-Figma chrome, including elements for features that are not behaviorally implemented. Removing a button because "we don't support that feature yet" is a fidelity bug, not a simplification.
3. **UI + engine + logger are co-developed per in-scope feature**, never in sequence. A feature is not "done" unless:
   - Engine operation exists and mutates the scene graph
   - UI control exists and is visually on-par with real Figma
   - Logger emits the corresponding semantic event
   - All three are tested together
4. **Scope discipline.** If a feature drifts toward functionally-out-of-scope territory, the drift is recorded as an open question rather than silently implemented. Adding visual UI for a §3 item is *not* a scope drift — it is the required baseline.
5. **Vertical slices over horizontal layers.** We do not "finish all UI, then all engine". Each slice ships one feature end-to-end.
6. **Docs are the source of truth for behavior; images are the source of truth for appearance.** Neither replaces the other.
7. **Honesty over polish.** When a gap, risk, or unknown exists, we record it. We do not silently paper over it.

## 5. Strategy — high level phases

| Phase | What happens | Artifacts produced |
|---|---|---|
| **1. Planning (now)** | Write the 5 `plan/*.md` docs; agree on each before moving on | `plan/00` through `plan/04` |
| **2. Extraction** | Run the two research agents over `helper/figma_docs` | `extracted/ui-schema/` + `extracted/features/` |
| **3. Engine skeleton + first slice** | Pick tech stack; set up project; implement Slice 0 (canvas + rectangle + selection + move + copy/paste + logger) | `src/` initial tree; working Slice 0 |
| **4. Feature-by-feature slicing** | Iterate through the slice list from `plan/04-build-phases.md`; each slice is a review checkpoint | Incremental slices on top of Slice 0 |

Phase boundaries are hard gates — no phase starts until the previous phase's artifacts are reviewed and signed off.

## 6. Roles

| Role | Responsibility |
|---|---|
| **Agent A — Feature researcher** | For a given feature (or batch of related features), reads relevant `helper/figma_docs` articles and produces a structured behavior spec. Never writes code. |
| **Agent B — UI schema researcher** | Reads `helper/figma_docs` articles + images to produce a structured UI schema: regions, states, reference images, measurements where derivable. Never writes code. |
| **Primary agent (me)** | Orchestrates: writes plan docs, dispatches A and B, integrates their outputs, designs the engine, writes the code, runs the build. |
| **User** | Reviews each plan doc, approves phase transitions, acts as scope guardian, fills gaps that extraction cannot cover (e.g., provides an ad-hoc screenshot of a UI state not in the corpus). |

## 7. Artifact map

```
figma-mock/
├── CLAUDE.md                 project instructions (source of truth for scope)
├── helper/
│   ├── figma_docs/           216 scraped articles + 1087 images (read-only)
│   └── analysis/             5 synthesized docs (read-only)
├── open-source-example/      OpenPencil reference (read-only)
├── plan/                     ← this directory; planning phase output
│   ├── 00-overview.md
│   ├── 01-ui-schema-extraction.md
│   ├── 02-feature-research.md
│   ├── 03-engine-architecture.md
│   └── 04-build-phases.md
├── extracted/                ← extraction phase output
│   ├── ui-schema/            Agent B output
│   └── features/             Agent A output
├── reference/                ← gap-fill screenshots (populated as needed)
└── src/ (or app/)            ← code (created after tech stack decision)
```

## 8. Decision log

### Decided

- **Scope:** Tier 2 feature set (see §2).
- **Out of scope:** listed in §3.
- **Build order:** vertical slices, per-feature.
- **UI fidelity source:** docs + images, not live Figma inspection (unless filling a gap).
- **Planning gate:** no code before all 5 plan docs are approved.

### Open (to be resolved in later plan docs or explicitly)

- **Tech stack**: framework (React / Vue / Svelte / Solid / vanilla), state management, build tool. → resolved in `plan/03-engine-architecture.md`.
- **Canvas rendering approach**: Canvas 2D, SVG, WebGL, canvaskit-wasm. → resolved in `plan/03-engine-architecture.md`.
- **Theme**: dark or light for MVP (only one). → needs explicit user decision before extraction begins, because the extracted schema should reference the correct theme.
- **Project package layout**: monorepo vs single package, module boundaries. → resolved in `plan/03-engine-architecture.md`.
- **Log storage + export format**: in-memory, IndexedDB, file download, WebSocket. → resolved in `plan/03-engine-architecture.md`.
- **Logger event taxonomy shape**: registry vs closed set, versioning. → resolved in `plan/03-engine-architecture.md`.
- **No-op UI click behavior**: clicking a §3 (visual-only) element — silent no-op, toast, disabled cursor, logger event emission semantics. → resolved in `plan/03-engine-architecture.md`.
- **Fonts**: Inter from Google Fonts vs locally bundled. → resolved in `plan/03-engine-architecture.md`.
- **Icons**: extracted from Figma UI kit (if locatable) vs Lucide-with-replace-later. → resolved in `plan/01-ui-schema-extraction.md`.

## 9. Review cadence

- **Per plan document (`plan/00` through `plan/04`)**: user reviews, approves or sends back with edits, before the next doc begins.
- **Phase transitions (1→2, 2→3, 3→4)**: user approves explicitly.
- **Per vertical slice (phase 4)**: user runs the slice, verifies it against the corresponding reference images, approves or sends back.
- **Mid-slice questions**: raised immediately rather than deferred. No silent assumptions.
