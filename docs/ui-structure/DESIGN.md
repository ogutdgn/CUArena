# Word UI-Structure Extraction Pipeline ("ui-crawl") — Design

**Status:** Design approved 2026-07-05 (brainstormed + twice adversarially audited; see §12).
**Owner docs:** this file. Output ground truth will live in `parity/oracle/ui-structure/`.
**Parity target:** live MS Word for Windows, M365 Current Channel x64 en-US, build 16.0.20026.20168
(ADR-0006). Live Word is the ONLY source of truth; Microsoft's official control inventory is
verification-only (D9).

---

## 1. Purpose

Crawl the **live** MS Word application and emit a complete, machine-readable JSON structure of its
entire UI — every section, tab, group, control, popup, dialog, pane, and on-canvas affordance —
so that:

1. the UI can be **faithfully replicated** (labels, icons, tooltips, keytips, control types,
   split-button zones, gallery layouts, pixel geometry), and
2. every control can later be **bound to a document engine** (via the `idMso` bridge field).

**No-gap guarantee:** every press either resolves to a captured surface (`ref`) or terminates at a
declared **boundary** (`excluded` / `deferred`, each tied to a recorded decision). There is no third
state. Completion = frontier empty + every node `complete | blocked(reason) | boundary`.

## 2. Core concepts

- **Surface graph, not a tree.** Nodes are UI surfaces (shell sections, ribbon tabs, popups,
  dialogs, dialog tab-pages, panes, canvas trigger-states). Edges are "press → opens". Shared
  surfaces (e.g. the Font dialog) are defined **once** and referenced; each surface carries an
  `entry_points[]` reverse index.
- **Frontier ledger.** Every discovered-but-not-yet-captured surface sits in the frontier
  (journal-backed). The crawl is done when the frontier is empty.
- **Boundary markers.** Scope edges are explicit data, never silent omissions (see §4.3).
- **Hybrid execution.** A deterministic, journaled Python crawler (pywinauto/UIA) does the walking;
  agents adjudicate ambiguity from journal evidence (screenshots + UIA dumps), never by ad-hoc live
  clicking.

## 3. Scope

### 3.1 In scope (v1)

| Area | Contents |
|---|---|
| Shell header | Title bar: AutoSave toggle, Save, Undo/Redo, QAT + its customize menu, document title (+ rename flyout), search box (+ suggestions flyout), account area, Ribbon Display Options, window buttons. Tab-row right cluster: Comments, Editing-mode dropdown, Share, Add-ins (D1 amendment). |
| Shell footer | Status bar default segments: page indicator, word count (→ dialog), proofing icon (→ pane), language, focus, view switcher, zoom-out, **zoom slider**, zoom-in, zoom % (→ dialog). |
| Page chrome | Rulers (incl. tab-stop cycle selector, drag targets, double-click → Page Setup), scrollbars, collapse-ribbon chevron. Shallow: geometry + interactions, no document content. |
| Ribbon | All core tabs + **all contextual tabs** via recipes (§7). Every control fully captured. |
| Popups | Every dropdown/menu/gallery/color-grid/size-grid/form-flyout reachable from any in-scope control, recursively (submenu chains included). |
| Dialogs | Every dialog reachable from any in-scope control, recursively (child dialogs included), incl. per-tab pages, expansion states (More >>), and a **stimulus pass** (§8.4). |
| Panes | Every task pane reachable from controls; pane internals captured with the pane schema. |
| On-canvas UI | Floating buttons (Layout Options, Paste Options, AutoCorrect lightning, chart trio, equation chevron, comment cards, Welcome-back) + **handle sets** (resize-8, rotate, table-set, adjustment-diamonds, gizmo-3d, crop-set) defined once and referenced per trigger (D2). |
| Screenshots | One canonical PNG per surface state + `bounds` on every control (D10, §5.6). |

### 3.2 Boundaries (decisions D3–D8)

| Policy | Edge | Decision |
|---|---|---|
| `excluded` | File → backstage (button documented, never entered) | D4 |
| `excluded` | Developer tab (not enabled, not captured) | D4 |
| `excluded` | View-mode shells beyond their buttons (Read Mode, Web Layout, Outline, Draft, Immersive Reader, Focus) — buttons fully documented with `switches-view-mode` + boundary | D3 |
| `excluded` | Responsive/collapsed-ribbon window states; capture is pinned maximized (groups collapsed **at baseline** ARE captured via `group-overflow`) | D7 |
| `excluded` | OS/out-of-process windows (Help, VBA editor, OS consent prompts), feature-spawned floating toolbars (Dictate), cloud-gated surfaces (Designer, Copilot, sign-in flows) — cloud-gated presence recorded in manifest | D8 |
| `deferred` | All right-click surfaces: context menus, mini toolbar, gallery-tile right-click menus | D6 |
| `deferred` | Non-default status-bar segments (only reachable via right-click Customize) | D6 |
| `deferred` | Handle visual-capture residue, if any survives P3 | D2 |

Every boundary edge appears in `coverage.json` under its decision id. Flipping a boundary later
(e.g. crawling backstage) is a data change, not a schema change.

### 3.3 Decision register (all dated 2026-07-05)

| Id | Decision |
|---|---|
| D1 | Scope = visible app shell + ribbon (incl. all contextual tabs) + everything reachable from controls; incl. the tab-row right cluster (Comments/Editing/Share/Add-ins) |
| D2 | On-canvas UI in v1: floating buttons + all handle sets, defined once in `canvas/handle-sets.json` and referenced per trigger |
| D3 | View-mode shells beyond their buttons: excluded (buttons documented with boundary) |
| D4 | Backstage never entered (File button documented); Developer tab not enabled/captured |
| D5 | Contextual recipe list includes Graphics Format (SVG), 3D Model, Ink — all 17 tabSets accounted for |
| D6 | Right-click surfaces + non-default status-bar segments: deferred, named in coverage |
| D7 | Fixed capture environment (maximized 1920×1080, 100 % DPI); no responsive/collapsed-ribbon variants |
| D8 | OS windows / VBA / Help / feature-spawned floating toolbars / cloud-gated surfaces: excluded or blocked-adjudicated |
| D9 | Official Microsoft control inventory is verification-only; live Word adjudicates every dispute |
| D10 | Screenshots are committed first-class artifacts; every control carries `bounds` into its surface screenshot |

### 3.4 Environment pin

Maximized 1920×1080, 100% DPI, light Office theme, en-US, Print Layout, add-ins disabled at launch,
first-run nags/teaching callouts suppressed by policy + a known-nag window filter, Office updates
frozen (registry) and Windows Update paused for the run window, build asserted via COM at every
Word (re)launch. All pins recorded in `manifest.json`.

## 4. Data model

### 4.1 Control (the universal node)

```json
{
  "id": "ribbon.home.paragraph.numbering",
  "label": "Numbering",
  "tooltip": "…",
  "keytip": "N",
  "shortcut": null,
  "type": "split",
  "icon": "icons/ribbon/home/numbering.png",
  "bounds": { "in": "screenshots/ribbon/home.png", "x": 214, "y": 66, "w": 26, "h": 24 },
  "primary": { "action": { "kind": "feature", "note": "applies last-used numbering (toggle)" } },
  "flyout":  { "action": { "kind": "opens-dropdown", "ref": "dropdowns/numbering-library" } },
  "idMso": "NumberingList",
  "enabled_in": { "blank": true, "table-selected": true, "picture-selected": false },
  "stateVariants": null,
  "capture": { "status": "complete", "probe_mode": "pressed-observed",
               "evidence": "journal://…", "build": "16.0.20026.20168", "schema_version": 1 }
}
```

- **`type` enum:** `button | toggle | split | dropdown | menu | gallery | combo | spinner |
  checkbox | launcher | label | slider | text-input | group-overflow`.
  - `dropdown` = value selector showing current value; `menu` = command list opener (distinct).
  - `combo` carries `editable` + value domain; `spinner`/`slider` carry
    `{min, max, step, unit, detents?, buttonStep?}` (slider values read from UIA RangeValuePattern).
  - Mutually exclusive toggle sets (e.g. view switcher) share a `toggleGroup` id.
- **`split`** controls have two zones (`primary` + `flyout`), each with its own tooltip/action;
  the primary zone may itself be a toggle.
- **`gallery`** controls may carry an **`inRibbon`** block for in-ribbon strips (Styles, Table
  Styles): visible tile window (refs into the popup's item list — no duplication), tilesPerRow,
  tile size, `directApply`, `hoverLivePreview`, selection highlight, and the three strip buttons
  (scroll-up / scroll-down / more, each its own hit target; `more` opens the popup file).
- **`group-overflow`**: the chevron of a group collapsed at baseline (e.g. Home → Editing);
  `groupRef` points at the owning group; action `opens-group-flyout`. The flyout hosts the group's
  own child controls (same ids — ownership stays with the group; coverage counts each control once).
- **`stateVariants`**: for controls whose icon/label/primary action changes with runtime state
  (Font Color's last-color bar, AutoSave on/off, Undo enablement). Live-data shell text
  ("Page 3 of 12", word count) is captured as a template with bound variables.
- **`keytip`**: captured for every ribbon control (Alt overlay).
- **`bounds`**: pixel rect inside the owning surface screenshot (§5.6).
- **`idMso`**: read live from UIA `AutomationId` where Word exposes it (pilot verifies the
  equivalence); never sourced from the offline inventory. This is the engine-binding bridge.
- **`capture.probe_mode`**: `pressed-observed | pattern-inferred | boundary-declared` — an honest,
  first-class record of HOW the classification was obtained (§6.3).

### 4.2 Action

```json
"action": {
  "kind": "feature | toggles | opens-dropdown | opens-menu | submenu | opens-dialog |
           opens-pane | opens-group-flyout | activates-tab | cycles-state |
           switches-view-mode | opens-backstage",
  "ref": "dialogs/font",
  "boundary": { "policy": "excluded | deferred", "reason": "…", "decision": "D3" }
}
```

`ref` XOR `boundary` for every opening kind. `feature` classification requires **positive
evidence** (doc-hash delta, COM app-state delta, or toggle-state change); with no observed effect
the node goes to the ambiguous queue as `unresolved` — silent "feature" completions are forbidden.
`activates-tab` refs target a ribbon tab surface id (e.g. `ribbon/table-design`); the target tab
file carries its own contextual/recipes block, so the edge needs no recipe qualification.

### 4.3 Popup file (`dropdowns/<id>.json`)

```json
{
  "id": "dropdowns/numbering-library",
  "entry_points": ["ribbon.home.paragraph.numbering.flyout"],
  "screenshot": "screenshots/dropdowns/numbering-library.png",
  "sections": [
    { "title": "Numbering Library", "kind": "gallery",
      "layout": { "columns": 3, "tile": { "w": 80, "h": 68 } },
      "items": [ { "id": "…", "preview": "icons/…png", "selected": false,
                   "action": { "kind": "feature" } } ] },
    { "kind": "menu-items", "items": [
        { "label": "Define New Number Format…", "icon": null,
          "action": { "kind": "opens-dialog", "ref": "dialogs/define-new-number-format" } } ] }
  ],
  "hoverLivePreview": true,
  "capture": { "…": "…" }
}
```

- **Section kinds:** `gallery | menu-items | color-grid | size-grid | controls | form`.
  - `color-grid`: theme row + tint/shade columns + standard row + trailing menu items
    (More Colors… → dialog ref).
  - `size-grid`: hover-dimension matrix (Insert → Table 10×8) with live cell highlight semantics.
  - `controls`: sections hosting **full Control objects** (collapsed-group flyouts, rich flyouts).
  - `form`: input-bearing flyouts (title rename, search suggestions) — fields use the dialog
    field vocabulary.
- **Item flags:** `checked`/`radio` state, `selected` (current-value highlight), `ownTypeface`
  (font list renders in own font), two-line descriptions, `submenu` items MUST carry a `ref`.
- **Item ids:** every item in EVERY section kind carries a required, popup-unique `id` slug;
  external references address items as `<popup-id>#<item-id>`
  (e.g. `dropdowns/numbering-library#decimal-1`) — see §4.8.
- **`dynamic: true`** marks machine-varying sections (Recently Used, MRU fonts, document-derived
  styles). Dynamic sections are excluded from the determinism diff; their capture records what was
  visible plus the generation rule.

### 4.4 Dialog file (`dialogs/<id>.json`)

```json
{
  "id": "dialogs/font",
  "title": "Font",
  "modal": true,
  "entry_points": ["ribbon.home.font.launcher", "dialogs/modify-style#btn:format-font"],
  "identity": { "signature": "sha256:…", "note": "structural signature, not title (§5.3)" },
  "tabs": [
    { "name": "Font", "screenshot": "screenshots/dialogs/font@font.png",
      "sections": [
        { "title": "Effects", "fields": [
            { "name": "Strikethrough", "type": "checkbox", "tristate": true,
              "bounds": { "…": "…" } },
            { "name": "Size", "type": "combo", "editable": true,
              "values": ["8","9","…"], "unit": "pt" },
            { "name": "Font color", "type": "color-picker",
              "moreRef": "dialogs/colors" } ] } ] }
  ],
  "buttons": [
    { "name": "Text Effects…", "action": { "kind": "opens-dialog", "ref": "dialogs/format-text-effects" } },
    { "name": "Set As Default", "action": { "kind": "opens-dialog", "ref": "dialogs/set-default-confirm" } },
    { "name": "OK", "role": "default" },
    { "name": "Cancel", "role": "cancel" }
  ],
  "expansion": null,
  "dependencies": [ { "if": { "field": "#field:line-spacing", "op": "in",
                              "values": ["At least", "Exactly", "Multiple"] },
                     "enables": ["#field:at"] } ]
}
```

- **Field types:** `text | combo | listbox (itemized + selection mode) | checkbox (tristate-capable)
  | radio-group (mutual exclusion explicit) | spinner/measurement (unit, range, step, blank-allowed)
  | color-picker | slider | preview-pane (non-interactive render) | interactive-preview
  (display+edit widget, e.g. Borders & Shading edge diagram) | button`.
- Fields map to their **tab page and visual section** (never a flat list). Section groupings are
  authored by the adjudication agent from screenshots (UIA gives a flat list), then sample-checked
  by a second agent (§8.7).
- Every body button carries an action/ref; default/cancel roles recorded. `expansion` captures
  More>>/Less<< states (each state gets its own screenshot).
- `dependencies` records enable-iff relations observed during the stimulus pass (§8.4).

### 4.5 Pane file (`panes/<id>.json`)

Same skeleton as popups (`sections`, kind `controls`/`form`), plus docking edge, close/pin
affordances, and internal search boxes/toolbars as full controls.

### 4.6 Canvas files

- **`canvas/handle-sets.json`** — shared, defined ONCE: `resize-8` (4 corners + 4 edges with
  axis/cursor per handle), `rotate`, `table-set` (✛ move, resize grip, ⊕ insert bubbles with
  `repeats: per-boundary`), `adjustment-diamonds` (`repeats: per-shape-geometry`), `gizmo-3d`,
  `crop-set` (replaces resize-8 in crop mode). Handles use
  `manipulation: {gesture, effect, axis?, cursor}` instead of / alongside `action`.
- **`canvas/<trigger>.json`** — per trigger state:

```json
{ "trigger": { "recipe": "picture-selected", "appears_on": "selection" },
  "handleSets": ["resize-8", "rotate"],
  "attachments": [
    { "id": "canvas.picture.layout-options", "role": "floating-button",
      "anchor": { "target": "selected-object", "position": "outside-top-right" },
      "action": { "kind": "opens-dropdown", "ref": "dropdowns/layout-options" },
      "capture": { "method": "uia" } } ],
  "screenshot": "screenshots/canvas/picture-selected.png" }
```

Notable set memberships: chart & SmartArt have **no** `rotate`; 3D uses `gizmo-3d`;
`capture.method: uia | visual` records whether the element is a real UIA control or a drawn
adornment documented from screenshots.

### 4.7 Ribbon tab file (`ribbon/<tab>.json`)

```json
{
  "id": "ribbon/home",
  "tabLabel": "Home",
  "keytip": "H",
  "contextual": null,
  "screenshot": "screenshots/ribbon/home.png",
  "groups": [
    { "id": "ribbon.home.editing",
      "label": "Editing",
      "bounds": { "in": "screenshots/ribbon/home.png", "x": 1710, "y": 4, "w": 96, "h": 88 },
      "launcher": null,
      "collapsedAtBaseline": true,
      "controls": [ "…Control objects (§4.1)…" ] }
  ],
  "capture": { "…": "…" }
}
```

- Contextual tabs fill `contextual`: `{ "tabSet": "Table Tools", "recipes": ["table-selected"] }`.
- Group ids follow the dotted convention (`ribbon.<tab>.<group>`); control ids nest under them.
  Groups carry their own label + bounds (group headers are addressable, croppable artifacts).
- A group's dialog launcher lives in its `launcher` slot (a Control of type `launcher`).
- When `collapsedAtBaseline` is true the group keeps its object and child controls (same ids);
  the chevron is a `group-overflow` Control whose `groupRef` is the group id string.

### 4.8 Identity & reference registry (normative)

**Identity rules:**

- **R1 — Surface ids** equal the output-root-relative path minus `.json`: `ribbon/home`,
  `dropdowns/numbering-library`, `dialogs/font`, `panes/navigation`, `canvas/picture-selected`.
  The §5 slug pipeline runs at **id-assignment time**; the filename is derived from the id, never
  the reverse — id and path cannot diverge.
- **R2 — Node ids** (groups, controls, canvas attachments) are dot-paths scoped under their
  surface: `ribbon.home.paragraph.numbering`, `ribbon.home.editing`,
  `canvas.picture.layout-options`. Globally unique, lowercase slugs. Reserved zone suffixes:
  `.primary` / `.flyout` (split zones), `.scroll-up` / `.scroll-down` / `.more` (inRibbon strip
  buttons). **Stability:** ids derive from tab/group + `idMso` where available (label slug only
  as fallback), so a label change between builds does not change the id.
- **R3 — Sub-surface addresses** use `<surface-id>#<local-id>`:
  `dropdowns/numbering-library#decimal-1` (popup item), `dialogs/font#tab:advanced`,
  `dialogs/font#field:size`, `dialogs/font#btn:text-effects`,
  `canvas/handle-sets#resize-8.nw` (handle-set member). Local ids are unique per surface.
- **R4 — Asset refs** (`icon`, `screenshot`, `preview`, `bounds.in`) are literal output-root-
  relative paths WITH extension and must appear in the matching hash manifest
  (`icons.json` / `screenshots.json`). `bounds.in` must equal the owning surface's screenshot
  (or one of its declared state variants).

**Reference registry** (kind · target · cardinality · dangling policy):

| Ref | Target | Card. | Dangling |
|---|---|---|---|
| `action.ref`, `moreRef`, submenu/button/attachment `ref` | surface id (R1) | 0–1 | hard-fail |
| `entry_points[]` | node id (R2, zone-suffix allowed) or sub-surface address (R3) | N | hard-fail |
| `groupRef` | group id (R2) | 1 | hard-fail |
| `inRibbon.visibleItemRefs[]` | item local-ids within the owning popup (R3 local part) | N | hard-fail |
| `handleSets[]` | set keys in `canvas/handle-sets.json` | N | hard-fail |
| `icon` / `screenshot` / `preview` / `bounds.in` | asset path (R4) | 0–1 | hard-fail |
| `toggleGroup` | opaque id, unique per surface | 0–1 | n/a |
| `trigger.recipe`, `enabled_in` keys, `variants` keys | recipe id in `recipes.json` (`<recipe>[@<placement>]`) | N | hard-fail |
| `dependencies.if.field` / `enables[]` | `#field:` addresses within the same dialog (R3) | N | hard-fail |
| `boundary.decision` | D-register entry (§3.3) | 1 | hard-fail |
| `capture.evidence` | journal URI (archive URI after P4 per §5.1) | 1 | must resolve until archival |
| `idMso` | external bridge value — validated by DoD §8.3, not by this gate | 0–1 | n/a |

**Variants addressing:** inbound refs ALWAYS target the base surface id. A surface whose content
genuinely differs per context carries `variants` keyed by recipe id, with a mandatory `default`;
the consumer selects the variant matching its context, falling back to `default`. Refs never point
inside a variant.

**Integrity rules (enforced by the reconciling emitter on every emit, and a DoD gate):**

1. **Reference closure:** every reference of every registered kind resolves under its rule — zero
   dangling edges.
2. **`entry_points` inversion:** `entry_points` is generated by the emitter from the journal as
   the exact inverse of inbound refs — never hand-maintained.
3. **Boundary double-entry:** node-level `boundary` blocks and `coverage.json` edges are both
   emitter-generated from the same journal records (single source — they cannot disagree).
   Coverage edge format:
   `{ "from": "ribbon.file", "kind": "opens-backstage", "policy": "excluded", "decision": "D4" }`.

## 5. Output layout

```
parity/oracle/ui-structure/
  manifest.json            build, date, env pins, schema_version, coverage summary,
                           cloud-gated presence set, throughput stats
  shell.json
  ribbon/<tab>.json        home.json … table-design.json (contextual tabs too)
  dropdowns/<id>.json
  dialogs/<id>.json
  panes/<id>.json
  canvas/handle-sets.json  + canvas/<trigger>.json
  recipes.json             recipe registry: id, fixture path, selection placements (§7)
  icons/<tab-or-area>/…png + icons.json      (hash, size; fluent_name enrichment later)
  screenshots/<area>/…png  + screenshots.json (hash manifest)
  coverage.json            frontier state, boundaries by decision, deferred list, blocked list
```

1. **Committed:** all JSONs + icons + screenshots + coverage. **Not committed:** journal, UIA
   dumps, full-run evidence — these live in a scratch run dir outside OneDrive, are **retained
   until P4 acceptance**, then zipped to a local archive (journal is a hard dependency of resume,
   adjudication, and re-emit — it has a defined lifetime, not an ad-hoc one).
2. **`schema_version`** lives in the manifest and every file; journal entries are versioned;
   schema migrations ship with a journal-replay migrator (the schema WILL evolve after P0).
3. **Surface identity = structural signature** (normalized control-type/label tree, dynamic
   sections excluded), NOT window title. Same signature → same file, `entry_points` appended.
   Different content per context → `variants` block keyed by context. Title collisions (two
   different "Insert Cells" dialogs) get distinct ids.
4. **Slugging runs at id-assignment time** (lowercase, invalid chars stripped, length-capped,
   hash suffix on collision); filenames are derived from ids (R1, §4.8), never the reverse —
   id and path cannot diverge. NTFS case-insensitivity and MAX_PATH under the OneDrive path are
   handled; icons/screenshots are sharded into per-area subdirectories.
5. **Emitter is reconciling:** every emit regenerates the full output set from the journal and
   deletes orphans; a gate asserts manifest ↔ filesystem bijection (no unreferenced files, no
   missing files) AND **reference closure** per the §4.8 registry — every registered reference
   kind resolves under its rule, zero dangling edges, on every emit.
6. **Screenshots + bounds (D10):** one canonical PNG per surface state — full ribbon strip per
   tab (per recipe for contextual), each popup fully open (large galleries scroll-stitched), each
   dialog tab-page and expansion state, each pane, shell regions, each canvas trigger with handles
   visible. Taken clean (before child probing, no hover highlight). Every control's `bounds`
   locates it inside its surface screenshot — pixel-accurate layout for replication. Screenshots
   are excluded from the structural diff and compared by perceptual hash; a quality gate rejects
   blank/garbage frames.

## 6. Crawler architecture

Python package `docs/ui-structure/tools/` (pywinauto, UIA backend). Modules: **launcher** (COM,
PID-safe — kills only its own WINWORD PID), **enumerator**, **prober**, **icon-cropper**,
**screenshotter**, **tooltip-harvester** (UIA HelpText primary; hover fallback only while no popup
is open), **journal/frontier store** (JSONL, idempotent, resumable), **emitter**.

### 6.1 Press-mechanism rule (hard rule)

An unclassified control is **never** pressed via a synchronous in-proc path
(`InvokePattern.Invoke`, `LegacyIAccessible.DoDefaultAction`, `ExecuteMso`) — on modal-opening
controls the call blocks inside Word's UI thread and the prober deadlocks. Precedent recorded in
this repo: `parity/oracle/dump_dialog_uia.ps1` hit exactly this with ExecuteMso and switched to
SendKeys. Presses use **injected input only**: primary `click_input()` at the UIA bounding-rect
center (environment is pinned foreground/maximized), fallback keytip via SendInput. Synchronous
calls are allowed only on already-classified, known-non-modal targets (e.g. pressing Cancel to
dismiss a dialog).

### 6.2 Journal quarantine (anti-livelock)

`press-attempted(control)` is journaled BEFORE input injection. On resume, a press-attempted
without an outcome is not blindly re-pressed: after 2 attempts the control routes to the ambiguous
queue with the watchdog's pre-kill screenshot.

### 6.3 Pre-press resolution order

1. Edge carries a D1–D8 boundary → `probe_mode: boundary-declared`, action from the decision,
   **never pressed** (Dictate, Read Aloud, sign-in, Share-cloud flows, File, view-mode switches…).
2. UIA TogglePattern present → classify `toggle` without pressing (`pattern-inferred`); pressed
   only if stateVariants needs the alternate-state icon, under the symmetric-restore rule.
3. Otherwise → `pressed-observed`.

The pilot builds a **UIA exposure map** (which patterns Word actually exposes per control class —
split-button zone exposure, gallery item patterns, ScrollPattern availability) before trusting any
pattern heuristic at scale.

### 6.4 Visit choreography (one integrated visit per control)

Read properties (label, HelpText, patterns, AutomationId, bounds) → crop icon → press (per 6.1) →
observe → if a surface opened: screenshot it clean, enumerate + crop its children fully **while it
is open** (flyouts die on focus loss — no separate passes), bind popup→invoker (event order +
geometry adjacency + window-class heuristics; Office flyouts are ownerless "Net UI Tool Window"
HWNDs, same class as tooltips — ambiguous binds are re-opened twice to confirm) → close via
symmetric restore → verify baseline.

### 6.5 Observation & interlock

Adaptive window: 1.5 s baseline, extended for unclassified presses; wait-for-idle on window-count
stabilization. The next probe does not start until the desktop matches the baseline fingerprint —
late-arriving windows (slow panes, cloud surfaces) can never be attributed to the wrong control.
Known nag/teaching-callout window signatures are filtered from classification and logged.

### 6.6 Symmetric restore + app-state fingerprint

Toggles restored by re-press with ToggleState verified; panes closed by re-press or their Close
button (Esc does not close docked panes); menus/dialogs by Esc; document mutations by Ctrl+Z with
doc-hash verification. After every probe an **app-state fingerprint** is read via COM in one round
trip (TrackRevisions, View.Type, Zoom, DisplayRulers, formatting marks, open panes) — any drift
triggers restore + a flag on the probe record. Enumeration completeness guard: after enumerating a
flyout, child count is re-verified stable and the flyout still open; otherwise the node is marked
`partial` and retried, never silently complete.

### 6.7 Galleries & icon quality

Devirtualization by ScrollPattern where exposed, keyboard navigation fallback where not, with an
explicit convergence check (item set stable across two sweeps; recycled-element aware). Very large
machine-enumerated lists (font list) are captured as `dynamic` with the generation rule + the
machine's observed list. Icon crops target the glyph element where exposed; otherwise bbox crop +
label-trim post-processing; captured in non-hover state (mouse parked); PNG quality gate rejects
blank/garbage crops.

## 7. Context recipes (fixture-first)

A recipe = **open a pre-authored fixture .docx + select the object via COM** (creation-at-crawl
rejected: 3D insert wants online content, ink cannot be created via COM). Fixtures are authored
once (3D from a local .glb; ink drawn once by hand/injected input and saved) and committed under
`docs/ui-structure/tools/fixtures/`.

The recipe list is itself a machine artifact — `recipes.json` (recipe id, fixture path, selection
placements); `enabled_in` keys are `<recipe-id>` or `<recipe-id>@<placement>` drawn from it.

Recipes: `blank`, `text-selected`, `table-selected`, `picture-selected`, `shape-selected`,
`textbox-selected`, `equation-selected` (caret placed inside the OMath via COM),
`header-footer-active`, `smartart-selected`, `chart-selected` (Excel datasheet window closed as
part of setup), `icon-svg-selected` (Graphics Format), `3d-model-selected`, `ink-selected`,
plus mini-recipes `post-paste` (clipboard fixture set programmatically) and `autocorrect-hover`
(hover via UIA element reference, not coordinates).

- Recipe-list completeness is audited against the official inventory's 17 contextual tabSets:
  each tabSet has a recipe or a documented boundary/blocked reason.
- **Enablement semantics:** `enabled_in` is recorded per (recipe × defined selection placement)
  — "cursor inside table" is a different observation than "cursor beside table". Enablement is
  scanned in a **clean pass before any probing** in that recipe, so probe side effects cannot
  masquerade as recipe-level disablement.
- Each recipe run also fills the canvas checklist (which handle sets / floating buttons appear).

## 8. Verification — Definition of Done

1. **Frontier empty + reference closure.** Every node `complete | blocked(reason) |
   boundary(decision)`; every `opens-*` action has `ref` XOR `boundary`; no dangling reference
   of any §4.8-registered kind; `entry_points` is the journal-derived exact inverse of inbound
   refs.
2. **Reproducibility gate** (explicitly NOT a correctness axis): full second run → empty
   structural diff after normalization (account/doc name parameterized, `dynamic` sections and
   machine-enumerated lists excluded, icons/screenshots by perceptual hash).
3. **External oracle — ribbon layer only (stated limit):** official inventory
   (`parity/oracle/word_ribbon_inventory.json`, verification-only per D9) diffed by **idMso
   equality** (idMso read live from UIA AutomationId; the pilot validates this equivalence).
   Every "inventory has it, we don't" row adjudicated against live Word: added, or reasoned
   (not-in-this-build / hidden scope / boundary). Zero unexplained misses.
4. **Stimulus pass (in-dialog reactive discovery):** per dialog — every combo opened and
   enumerated, listbox entries walked, checkboxes toggled; revealed widgets and enable-iff
   dependencies recorded; per-dialog stimulus budget; budget exhaustion leaves an honest
   `partial`, never a silent complete.
5. **Sensor-diversity audit:** N surfaces independently re-extracted via a different sensor
   (agent-driven visual walk) and diffed against crawler output — the shared-sensor blind spot
   check for dialogs/popups/shell, which have no external inventory. The 7 pre-existing dialog
   captures (`parity/oracle/dialogs/*.json`) are a standing cross-check of the same kind.
6. **Screen-first visual sample audit:** samples drawn from the live screen → located in JSON
   (this direction catches missing nodes; JSON-first sampling cannot), stratified across the
   three `probe_mode` classes; sample size set by the acceptance target agreed at P4.
7. **Agent-judgment QA:** adjudications and dialog section-groupings sample-checked by a second
   independent agent; disagreements escalate to the user at phase gates.
8. **Asset gates:** every icon-bearing control has a non-garbage PNG; every dialog button has an
   action; manifest ↔ filesystem bijection holds.

## 9. Phases — each with its own exit gate

| Phase | Content | Exit gate |
|---|---|---|
| **P0** | Harness skeleton + **Home tab** end-to-end with its fixtures (clipboard, format-painter selection) | Home 100 % captured; UIA exposure map built; AutomationId=idMso validated; press-mechanism + reset rules proven; **throughput measured → full-run time budget**; schema ratified by the user on real data |
| **P1** | Remaining core tabs + shell (header/footer/rulers) | All core-tab + shell frontier resolved to refs/boundaries; per-tab checkpoint commits |
| **P2** | Popup/dialog frontier drain + stimulus passes | Frontier empty; ambiguous queue empty |
| **P3** | Context recipes → contextual tabs + their popups + canvas captures | All 17 tabSets resolved; canvas checklists complete |
| **P4** | Inventory diff + sensor-diversity audit + acceptance report | Full DoD (§8); report reviewed by the user |

Later phases (schema-ready, zero rework): backstage flip, right-click surfaces, any handle
visual-capture residue.

## 10. Risks (with mitigations designed in)

Synchronous-invoke deadlock (§6.1 — ExecuteMso precedent on record) · irreversible/app-level
probes (§6.3/6.6) · flyout death on focus loss (§6.4) · slow-surface misclassification (§6.5) ·
nag pollution (§3.3, §6.5) · gallery devirtualization convergence (§6.7) · ownerless-popup
misbinding (§6.4) · machine-varying content vs determinism (§8.2 normalization) · title-collision
identity (§5.3) · schema drift (§5.2 versioning) · orphaned outputs (§5.5 reconcile) ·
multi-day-run build drift (§3.3 freeze + per-launch assert) · Excel datasheet foreground theft
(§7) · OneDrive/NTFS path hazards (§5.4).

## 11. Relationship to the engine

The extraction is engine-agnostic. The binding hook is `idMso` on every control (live-read), plus
the action graph (control → surface → fields). A later "binding" pass maps `idMso`/action nodes to
engine capabilities (e.g. `WC.PM` command ids / `H[cmd]`); nothing in this pipeline depends on
that mapping, and no extraction data is sourced from the clone.

## 12. Provenance of this design

- Brainstormed interactively (2026-07-05); scope decisions D1–D10 recorded in §3.3.
- **Audit 1 (scope + data model):** 6-lens adversarial workflow, 75 agents — 70 raw → 69 unique
  findings, **67 confirmed** (each verified by an independent skeptic agent), 2 refuted. All
  confirmed amendments folded into §3–§4.
- **Audit 2 (pipeline §3–8):** 4-lens adversarial workflow, 44 agents — **37 confirmed**, 3
  refuted. All confirmed amendments folded into §5–§10.
- **Audit 3 (reference system):** 3-lens adversarial workflow, 27 agents — **21 confirmed**, 3
  refuted. Result: §4.7 (ribbon tab schema) + §4.8 (identity rules R1–R4, reference registry,
  variants addressing, integrity rules) and the reference-closure DoD gate.
- Ground-truth rule throughout: live Word adjudicates every dispute; the official inventory is
  verification-only (D9).
