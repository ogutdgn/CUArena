# P1: Knowledge Base Pipeline — Design

**Date:** 2026-07-07
**Status:** Approved design, pre-implementation
**Scope:** The first phase of the app-replication pipeline: building an accurate, structured knowledge base about a target application (e.g. "Microsoft Word", "Gmail") via live app inspection.

## Goal

Given the name of an application, produce a knowledge base accurate and complete enough that later pipeline phases can generate a replica of the application from it without guessing what the original does.

## A note on the examples

Examples throughout this spec use **Microsoft Word** as the benchmark target. This is deliberate: Word has one of the deepest, most complex UI surfaces in existence (ribbon tabs → groups → dropdowns → dialogs → panes → special tabs). If the pipeline can map Word, simpler apps (Gmail, Figma, …) follow much more easily. Nothing in this design is Word-specific: the pipeline is general and must be able to drive **any web or desktop application**.

## Core decisions

| Decision | Choice |
|---|---|
| Knowledge source | **Live app inspection** at every level. Model knowledge guides the explorer; the running app is ground truth. Web search supplies the usage signal for priority. |
| Platforms | Web + desktop apps. The KB schema is platform-agnostic; only the inspector backend differs (browser automation for web, OS accessibility/automation + vision for desktop). |
| Architecture | Staged pipeline with fan-out, structured as **two passes gated by priority**: breadth first, then depth only where priority justifies it. |
| KB format | Hybrid: structured JSON nodes (source of truth) + screenshots (visual evidence) + generated markdown overview (human review). |
| Storage | One JSON file per node, so parallel inspectors never conflict and git diffs show per-run changes. |
| Priority layers | Five fixed layers P0–P4. P0–P2 (high) documented at full depth, P3 (medium) at mid-level, P4 (low) stays at breadth. See "Priority layers and depth budgets". |

## The knowledge base

One graph per app: three node types, three edge types.

### Node types and rubrics

The rubric differs by level. Top level answers *what the app is*; lower levels answer *what each piece does*.

**`app` node (1 per KB) — anchor question: "What is this app?"**
- Identity: what it is, what it is used for, who uses it
- Skeleton: layout regions (sidebar, ribbon, canvas, panels…), menu map, navigation model
- Children: the feature inventory

**`feature` node — anchor question: "What is this feature doing?"**
- What it does (the function)
- How it is triggered (trigger paths — see edges)
- What it affects when it runs
- What it looks like (description + screenshot)
- Where it lives in the skeleton
- `audience_breadth`: who uses this — structured value: `everyone` / `most` / `niche` / `role-specific:<role>` (e.g. Track Changes → `role-specific:reviewer`). Feeds priority scoring.
- Children: sub-features

**`subfeature` node** — same anchor question and fields as `feature`, at finer grain. Detail smaller than a sub-feature (checkbox options, dropdown entries) is recorded **inside the node's fields** during the breadth pass, not as new nodes. The depth pass may expand genuine deeper structure for high-priority nodes only.

### Edge types

1. **`contains`** — hierarchy: app → feature → sub-feature. Fixed three levels in the breadth pass.
2. **`triggers`** — skeleton element → feature/sub-feature. Stored as the **full UI path**, since triggering is often multi-step: `Home tab → Font group → B button → Bold`. Dropdowns and dialogs appear as steps in these paths.
3. **`affects/uses`** — feature connections (from the original sketch). Allowed **between any two nodes at any level**: feature↔feature, sub↔sub, and cross-level (Gmail's search-by-label sub-feature ↔ Labels feature). These edges drive priority scoring, so restricting where they can exist would corrupt the ranking.

The skeleton and the features are connected *by construction*: every feature is triggered from somewhere in the skeleton. This connection is the backbone of both the completeness check and the skeleton depth rule below.

### UI element records — critical for UI replication

The pipeline must be UI-aware: the design and visual side of the app is knowledge, not decoration. Every UI element the inspector touches (in skeleton regions, trigger paths, and dialog contents) is captured as a structured record. **Control type, icon, and label are mandatory on every record** — they are the raw material for replicating the UI, and an element record missing them is incomplete:

```json
{
  "control_type": "toggle-button",
  "label": "Bold",
  "icon": { "description": "bold letter B", "image": "screenshots/bold-btn.png" },
  "tooltip": "Bold (Ctrl+B)",
  "shortcut": "Ctrl+B",
  "location": "Home tab > Font group",
  "state_notes": "highlighted when cursor is in bold text"
}
```

`control_type` captures the control's *behavioral* kind — button, toggle-button, dropdown, split-button, checkbox, radio, input, slider, tab… — not just its appearance. Icons get both a text description (for reasoning) and a cropped image (for pixel-faithful replication). Alongside the element records, general screenshots of each dialog, dropdown, and region are collected as visual evidence of composition and layout.

### Dialogs and dropdowns

Treated as first-class UI containers ("mini-skeletons"):
- They appear as steps in trigger paths.
- Their contents are enumerated: in the breadth pass, existence + purpose + rough contents; in the depth pass (priority-gated), every element inside is mapped to a sub-feature or recorded as a detail field.
- Each opened dialog gets its own screenshot.
- Element identification uses the DOM for web apps, the OS accessibility tree (e.g. Windows UI Automation) for desktop, with vision on screenshots as fallback.

### What is deliberately NOT in the KB

- **User flows / task sequences.** Not knowledge — derivable from a complete graph. Anything a task walk would reveal (state dependencies, orderings) belongs on the nodes as behavior knowledge.
- **KB testing machinery.** Verifying the knowledge is part of the larger pipeline but will be designed separately as its own component. P1's only built-in check is the structural completeness check below, which is a property of the graph itself.

### On-disk layout

```
kb/<app>/
  app.json
  features/<feature>.json
  subfeatures/<feature>/<sub>.json
  screenshots/<node-id>/*.png
  graph.json          # assembled graph + priority layers
  overview.md         # generated, human-readable
```

## The pipeline

Two passes, with priority as the gate between them. Breadth learns *what exists and how it is connected*; priority decides *what deserves deep knowledge*; depth exhausts only that.

**Stage 0 — Setup.** Resolve target app and platform; select inspector backend; handle access (account, install).

**Stage 1 — Skeleton pass.** One inspector opens the real app and maps the frame: identity, layout regions, menu map, navigation — and produces the **feature inventory** (level-2 list) with a trigger path for each entry. Model knowledge guides where to look; the live app is ground truth.

**Stage 2 — Breadth fan-out.** One inspector per feature, in parallel. Each fills the shallow rubric: what the feature does (briefly), its sub-features (level 3: names + one-liners), audience breadth, **connections (mandatory — priority depends on them)**, trigger paths, one screenshot. Wide, shallow, cheap.

**Stage 3 — Assembly + priority.** Merge node files into `graph.json`. Run the completeness check (below); unresolved gaps go back to Stage 2. Then rank every feature/sub-feature into the five layers P0–P4 from three signals:
1. **Connection density** — nodes with many `affects/uses` edges are structurally central (Font touches everything that renders text → P0).
2. **Real-world usage** — web search: what do users of this app actually use most.
3. **Audience breadth** — `everyone` outranks `niche` (Font vs. Mailings).

**Stage 4 — Depth fan-out.** Priority-gated. P0–P2 nodes each get an inspector that captures everything — every behavior, option, dialog, state, edge case, screenshots — descending until the depth endpoint rule (below) says stop. P3 nodes get the mid-level treatment defined in the depth budgets. P4 nodes are already done: breadth was their budget. Depth can be unbounded for P0–P2 *because* that set is small.

**Stage 5 — Finalize.** Recompute priority once (depth discoveries may promote features), regenerate `overview.md`, re-run the completeness check.

## Priority layers and depth budgets

Rankings map into **five fixed layers**. Each layer buys a defined amount of depth — this is what "high priority" concretely points to:

| Layer | Meaning | Knowledge depth | UI depth |
|---|---|---|---|
| **P0–P2** | High priority — the app's identity | Full: every behavior, option, state, edge case, documented exactly | Full: every dialog/dropdown along its trigger paths expanded, recursing until the depth endpoint rule fires |
| **P3** | Medium priority | Mid-level: all rubric questions answered thoroughly | Its direct UI containers (immediate dialogs/dropdowns) opened and enumerated **one level**, with screenshots — no recursion beyond that |
| **P4** | Low priority | Breadth-pass knowledge only (shallow rubric: name, one-liner, connections, trigger path) | Surface layer only: its top-level control exists with control type / icon / label; interiors stay `unexplored` stubs |

Where the score boundaries between layers fall is tunable and will be calibrated once real graphs exist.

### Depth endpoint rule — when does "as deep as it can" stop?

During deep exploration (P0–P2), an interaction chain is still **descending** while clicks keep opening more UI: another dialog, a new section inside the same dialog, another dropdown, a pane, a special tab. The chain reaches its **endpoint** when an element actually *triggers* a feature/sub-feature — i.e., performs an action on the app or document state instead of revealing more UI.

> Rule of thumb: **opens more UI → keep collecting. Fires an action → endpoint reached; record the trigger edge and stop.**

This gives every deep-dive inspector an unambiguous termination condition, no matter how deep the UI tree goes.

## Skeleton depth rule

The skeleton has the same explosion risk as features (Word's ribbon is a tree of dropdowns inside dialogs inside dropdowns). It gets the same two-pass treatment, with trigger edges as the mechanism that carries priority into the skeleton:

**Surface layer — always exhaustive, regardless of priority.** The app's top-level UI is documented completely and exactly: every visible control in the persistent chrome, plus the face of each primary navigation container opened once. In Word: **every ribbon tab, and every button on every tab's face** — each with its full `ui_element` record (control type, icon, label) and screenshots — including low-priority tabs like Mailings. Priority never gates the surface layer; it gates only what lies *below* it (dialogs, dropdowns, nested panes).

**Breadth stopping rule (measurable):** below the surface layer, expand a UI container only until every feature/sub-feature in the inventory has at least one complete trigger path. The metric is **trigger-path coverage**: expansion continues while coverage < 100% of the inventory and stops the moment it isn't. A container whose interior only holds deeper machinery gets a **stub**: name, purpose, one screenshot, marked `unexplored`.

**Depth rule:** skeleton detail rides on high-priority nodes. Deep-inspecting a P0 feature necessarily drags the inspector through its full trigger machinery, so every dropdown/dialog/panel **along that feature's trigger paths** gets fully enumerated. Deep skeleton knowledge = the union of the trigger paths of high-priority features, fully expanded.

**Consequence:** a skeleton element effectively inherits the priority of the features it triggers. The Font group's dropdowns get exhaustively mapped because P0 features pull them open; the Mailings tab's interior stays a stub because nothing high-priority ever pulls on it.

## Completeness check (three states)

For every interactive element found in expanded skeleton areas:

1. **Resolved** — maps to a known feature/sub-feature. ✓
2. **Unexplored** — a stub deliberately not expanded (low priority). Recorded and visible in the KB; not an error. Tells downstream phases "this area exists but we chose not to learn it."
3. **Gap** — should have resolved but didn't (a feature with no trigger path, or an element no feature claims). Goes back to inspection.

And in the other direction: every feature/sub-feature node must have at least one trigger path from the skeleton, or it is a gap.

## Definition of done (per app)

1. Completeness check passes: no gaps (unexplored stubs are allowed and labeled).
2. The skeleton surface layer is exhaustively documented (every top-level control with control type, icon, label, screenshots).
3. Every P0–P2 node has full-depth detail; every P3 node has mid-level detail. (P4 stays at breadth — by design, not omission.)
4. `graph.json` and `overview.md` generated and consistent with the node files.

## Out of scope for P1

- Testing/verifying the knowledge base (separate future component, own design)
- Downstream phases: planning, generation, verification of the replica
- The exact score boundaries between the five priority layers — tunable, calibrated empirically once real graphs exist
- Exact automation technology choices per backend (browser framework, desktop automation stack) — implementation-plan concerns
