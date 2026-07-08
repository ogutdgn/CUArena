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
| Web docs | Opportunistic and quality-gated. Docs guide inspectors and cross-check coverage but **never create nodes**; video-heavy or unstructured docs are deliberately skipped. |

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
2. **`triggers`** — skeleton element → feature/sub-feature. Stored as the **full UI path**, since triggering is often multi-step: `Home tab → Font group → B button → Bold`. Dropdowns and dialogs appear as steps in these paths. Paths are id-chains through the UI tree (see below), not prose strings. Keyboard shortcuts produce `triggers`/`opens` relationships too — they are the keyboard half of the trigger surface (see Shortcuts).
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
  "location": "ui:ribbon-home > ui:font-group",
  "triggers": "subfeature:bold",
  "state_notes": "highlighted when cursor is in bold text"
}
```

`control_type` captures the control's *behavioral* kind — button, toggle-button, dropdown, split-button, checkbox, radio, input, slider, tab… — not just its appearance. Icons get both a text description (for reasoning) and a cropped image (for pixel-faithful replication). Alongside the element records, general screenshots of each dialog, dropdown, and region are collected as visual evidence of composition and layout.

### The UI tree — containment and `opens` references

The UI itself is documented as a **tree of structured references in JSON**, not prose. Two relationships build it:

1. **Containment.** Dialogs, dropdowns, panes, menus, tabs, and sections are all technically the same thing: **UI containers**. Every container has an `id`, a `kind`, a screenshot, and `children[]` — the elements and nested containers inside it (a dialog's buttons, its sections, a section's controls).
2. **Opening.** When an element fires another piece of UI — a button inside a dialog opens another dialog, a dropdown opens a pane — the element records `"opens": "ui:<container-id>"`, a reference to the fired container.

Every interactive element carries **exactly one** of three markers, which turns the depth endpoint rule into a property of the data itself:

- `"opens": "ui:<container-id>"` — reveals more UI; descent continues into that container
- `"triggers": "<node-id>"` — fires a feature/sub-feature; this is an endpoint
- `"unexplored": true` — a stub below the priority budget

```json
// ui/font-color-dropdown.json
{
  "id": "ui:font-color-dropdown",
  "kind": "dropdown",
  "label": "Font Color",
  "screenshot": "screenshots/ui/font-color-dropdown.png",
  "children": [
    { "control_type": "swatch-grid", "label": "Theme Colors",
      "triggers": "subfeature:font-color" },
    { "control_type": "button", "label": "More Colors…",
      "opens": "ui:colors-dialog" }
  ]
}
```

Each container is one file (`ui/<container-id>.json`) referenced by id — never duplicated inline — because the same container is often reachable from several places (Word's Font dialog opens from the ribbon launcher *and* the right-click menu). Trigger paths are id-chains through this tree, so the chain dialog→dialog→dropdown→… that deep exploration walks is fully reconstructible from the data.

### Dialogs and dropdowns

All UI containers in the tree above ("mini-skeletons"):
- They appear as `opens` targets along trigger paths.
- Their contents are enumerated as `children[]`: in the breadth pass, existence + purpose + rough contents; in the depth pass (priority-gated), every child element is resolved to a sub-feature (`triggers`), a deeper container (`opens`), or a detail field.
- Each opened container gets its own screenshot.
- Element identification uses the platform's structured UI layer (the DOM on web, the OS accessibility tree on desktop), with vision on screenshots as fallback.

### Shortcuts — the keyboard trigger surface

The pipeline must capture keyboard shortcuts as knowledge: they are triggers without pixels. The skeleton is the app's *mouse* trigger surface; shortcuts are its *keyboard* trigger surface — two doors into the same rooms. A shortcut binding carries the same exactly-one-marker discipline as a UI element: it either `triggers` a feature/sub-feature (`Ctrl+B` → `subfeature:bold`) or `opens` a container (`Ctrl+F` in Word → the navigation pane).

What shortcuts have that buttons don't is **context**: the same key acts differently in different places (`Escape` closes a dialog / collapses a selection; `F2` edits a cell in Excel but does nothing in Word's ribbon). Every binding therefore records *when* it is active, not just *what* it does.

**Storage — the registry is the source of truth; nodes carry display references:**

```json
// shortcuts/ctrl+b.json — one file per key combination
{
  "keys": "Ctrl+B",
  "bindings": [
    {
      "context": "editing text / text selected",
      "effect": "toggles bold on selection or at cursor",
      "triggers": "subfeature:bold",
      "source": ["tooltip", "docs"]
    }
  ]
}
```

- The `shortcuts/` registry owns the facts: context (*when*), effect (*how it acts*), and exactly one action marker (*what it affects*) per binding. Context-dependent keys like `Escape` hold several bindings in one file.
- Feature/sub-feature nodes and `ui_element` records keep only the display string (`"shortcut": "Ctrl+B"`, harvested from tooltips) as evidence — a label, not a definition.
- Harvesting is defined at capability level, not tool level: shortcuts surface through element properties exposed by the platform's structured UI layer, tooltips, menu item labels, in-app shortcut reference panels, and web documentation. They are collected during the **breadth pass** (cheap — they appear on surfaces already being scanned); deep verification of subtle context behavior is priority-gated like everything else. Brute-force key-pressing is a last resort, not a method.
- **No separate depth policy.** Shortcut coverage is inherited from exploration depth: shortcuts sit on surfaces the pipeline is already scanning, so priority-gated digging (surface layer for everyone, full trigger machinery for P0–P2) automatically determines which shortcuts are found. The exception is bulk sources — an in-app shortcut reference panel or a documentation shortcut page — which are harvested once, opportunistically, across all priorities; a binding known only from docs (never observed live) keeps that provenance in `source`.
- **Checks that come free:** every binding must point at an existing node/container; a node whose display string has no matching registry entry is a gap; two bindings claiming the same key+context is a conflict flag.

### What is deliberately NOT in the KB

- **User flows / task sequences.** Not knowledge — derivable from a complete graph. Anything a task walk would reveal (state dependencies, orderings) belongs on the nodes as behavior knowledge.
- **KB testing machinery.** Verifying the knowledge is part of the larger pipeline but will be designed separately as its own component. P1's only built-in check is the structural completeness check below, which is a property of the graph itself.

### On-disk layout

```
kb/<app>/
  app.json
  features/<feature>.json
  subfeatures/<feature>/<sub>.json
  ui/<container-id>.json        # UI tree: containers with children[] and opens references
  shortcuts/<keys>.json         # shortcut registry: context-scoped bindings (source of truth)
  docs/<page>.md                # harvested official docs (only when the quality gate passes)
  docs-tree.json                # cross-page reference tree from the docs
  screenshots/<node-id>/*.png
  graph.json          # assembled graph + priority layers
  overview.md         # generated, human-readable
```

## The pipeline

Two passes, with priority as the gate between them. Breadth learns *what exists and how it is connected*; priority decides *what deserves deep knowledge*; depth exhausts only that.

**Stage 0 — Setup.** Resolve target app and platform; select inspector backend; handle access (account, install).

**Stage 1 — Skeleton pass.** One inspector opens the real app and maps the frame: identity, layout regions, menu map, navigation — and produces the **feature inventory** (level-2 list) with a trigger path for each entry. Model knowledge guides where to look; the live app is ground truth.

**Stage 1b — Docs harvest (parallel with Stage 1; opportunistic and quality-gated).** Search the web for official documentation about the target app. Harvest **only** if it passes a quality gate: official source, current, **text-based and structured** enough to map pages to features. Existence is not sufficient — MS Word has extensive docs, but they are sprawling and mostly video, which is worthless to this pipeline; that case fails the gate. Failing the gate is recorded as a deliberate skip and the pipeline continues unchanged — it never depends on docs. When harvested: each page becomes markdown (text, links, images) under `docs/`, and cross-page references become `docs-tree.json` — the vendor's own map of feature relationships.

Docs **guide, never create**: no feature/sub-feature node is ever created from documentation. Three uses: (1) inspectors read the relevant pages before exploring a feature, so they know what to look for; (2) Stage 3 runs a docs coverage cross-check; (3) evidence — shortcut pages, and cross-references corroborating `affects/uses` edges. All docs-sourced facts carry `"source": "docs"`, and the standing law applies: **docs inform, the live app confirms** — conflicts resolve in favor of the live app and the doc claim is flagged stale.

**Stage 2 — Breadth fan-out.** One inspector per feature, in parallel. Each fills the shallow rubric: what the feature does (briefly), its sub-features (level 3: names + one-liners), audience breadth, **connections (mandatory — priority depends on them)**, trigger paths, one screenshot. Wide, shallow, cheap.

**Stage 3 — Assembly + priority.** Merge node files into `graph.json`. Run the completeness check (below); unresolved gaps go back to Stage 2. If docs were harvested, also run the **docs coverage cross-check**: a feature named in the docs but absent from the inventory is a candidate gap — investigated live before anything is added. Then rank every feature/sub-feature into the five layers P0–P4 from three signals:
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

In the data this is literal: descending = writing `opens` references and recursing into new container files; endpoint = writing a `triggers` reference. This gives every deep-dive inspector an unambiguous termination condition, no matter how deep the UI tree goes.

## Skeleton depth rule

The skeleton has the same explosion risk as features (Word's ribbon is a tree of dropdowns inside dialogs inside dropdowns). It gets the same two-pass treatment, with trigger edges as the mechanism that carries priority into the skeleton:

**Surface layer — always exhaustive, regardless of priority.** The app's top-level UI is documented completely and exactly: every visible control in the persistent chrome, plus the face of each primary navigation container opened once. In Word: **every ribbon tab, and every button on every tab's face** — each with its full `ui_element` record (control type, icon, label) and screenshots — including low-priority tabs like Mailings. Priority never gates the surface layer; it gates only what lies *below* it (dialogs, dropdowns, nested panes).

**Breadth stopping rule (measurable):** below the surface layer, expand a UI container only until every feature/sub-feature in the inventory has at least one complete trigger path. The metric is **trigger-path coverage**: expansion continues while coverage < 100% of the inventory and stops the moment it isn't. A container whose interior only holds deeper machinery gets a **stub**: name, purpose, one screenshot, marked `unexplored`.

**Depth rule:** skeleton detail rides on high-priority nodes. Deep-inspecting a P0 feature necessarily drags the inspector through its full trigger machinery, so every dropdown/dialog/panel **along that feature's trigger paths** gets fully enumerated. Deep skeleton knowledge = the union of the trigger paths of high-priority features, fully expanded.

**Consequence:** a skeleton element effectively inherits the priority of the features it triggers. The Font group's dropdowns get exhaustively mapped because P0 features pull them open; the Mailings tab's interior stays a stub because nothing high-priority ever pulls on it.

## Completeness check (three states)

Because every interactive element must carry exactly one of the three markers (`triggers` / `opens` / `unexplored`), this check is **mechanical** — it walks the UI tree and inspects the data:

1. **Resolved** — the element has `triggers` (maps to a known feature/sub-feature) or `opens` (leads into a documented container). ✓
2. **Unexplored** — marked `unexplored: true`: a stub deliberately not expanded (low priority). Recorded and visible in the KB; not an error. Tells downstream phases "this area exists but we chose not to learn it."
3. **Gap** — an element with none of the three markers, an `opens` reference to a container file that doesn't exist, or a feature with no trigger path. Goes back to inspection.

The shortcut registry is checked the same way: a binding pointing at a missing target, a node display string with no registry entry, or two bindings claiming the same key+context — all flagged as gaps/conflicts.

And in the other direction: every feature/sub-feature node must have at least one trigger path from the skeleton, or it is a gap.

## Inspector tool catalog

Inspectors operate from a **curated catalog of vetted, trustworthy tools** — they never improvise their own tooling. The catalog is the pipeline's statement of what is trusted to produce knowledge.

**Entry criteria — what "trustworthy" means concretely:**
1. Returns **structured data, not guesses** (vision is the one labeled exception, admitted only as fallback).
2. Enforces **safety internally**: destructive-action blocklist (Send, Delete, Purchase, Share…) and dedicated test accounts/documents — an inspector exploring Gmail can never actually send an email, and Word inspection happens on scratch documents.

**v1 catalog:**

| Platform | Tool | Role |
|---|---|---|
| Desktop (Windows) | UI Automation (UIA) | Workhorse: element trees, labels, control types, states, accelerator keys; drives controls via native patterns (invoke, toggle, expand). The same API screen readers rely on, so vendors keep it working. |
| Desktop | Screen capture | Screenshots, region shots, icon crops |
| Desktop | Input injection | Mouse/keyboard events where native patterns can't drive |
| Desktop | Vision fallback | Screenshot + model interpretation, only where the accessibility tree is poor |
| Web | Browser automation (CDP/Playwright-class) | DOM + ARIA snapshots, click/hover/type, screenshots, `aria-keyshortcuts` — the web equivalent of UIA |
| Research | Web search + page-fetch-to-markdown | Usage signal for priority; docs harvest |
| KB | Schema-enforcing writers | Write nodes/containers/shortcuts; refuse malformed records (missing icon/label, zero-or-two action markers) — schema discipline is guaranteed by the tool, not by agent judgment |

**Provenance.** Every fact in the KB records which tool produced it (`"source": "uia"` / `"vision"` / `"docs"` / `"tooltip"`). Structured sources are strong evidence; vision-only or docs-only facts are weaker and are standing candidates for re-verification. Trust in tools becomes measurable trust in knowledge.

Other desktop platforms follow the same pattern through their native accessibility APIs and can be added to the catalog without any schema change.

## Definition of done (per app)

1. Completeness check passes: no gaps (unexplored stubs are allowed and labeled).
2. The skeleton surface layer is exhaustively documented (every top-level control with control type, icon, label, screenshots).
3. Every P0–P2 node has full-depth detail; every P3 node has mid-level detail. (P4 stays at breadth — by design, not omission.)
4. `graph.json` and `overview.md` generated and consistent with the node files.

## Out of scope for P1

- Testing/verifying the knowledge base (separate future component, own design)
- Downstream phases: planning, generation, verification of the replica
- The exact score boundaries between the five priority layers — tunable, calibrated empirically once real graphs exist
- Exact library/wrapper choices and API design for the catalog tools — implementation-plan concerns (the catalog names *what* is trusted; the plan decides *how* each tool is built)
