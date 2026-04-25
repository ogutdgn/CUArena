# Plan 01 — UI Schema Extraction (Agent B)

## 1. Purpose

Agent B reads the Figma documentation corpus (`helper/figma_docs/` articles + images) and produces a structured UI schema under `extracted/ui-schema/`. The schema tells the build phase *what UI elements exist*, *where they live*, *what states they have*, and *which reference image shows each state*.

Agent B does **not** write code, does **not** extract pixel measurements, does **not** sample hex color codes, does **not** produce mockups. It catalogs and cross-references.

## 2. Inputs

Agent B reads from (in priority order):

1. **`helper/figma_docs/articles/Figma Design/`** — all 175 Figma Design articles. Each article has `content.md`, `metadata.json`, and an `images/` folder.
2. **UI-focused articles to read first** (highest reference density):
   - `navigating-ui3/` (54 images — canonical UI3 overview)
   - `access-design-tools-from-the-toolbar/` (toolbar)
   - `view-layers-and-pages-in-the-left-sidebar/` (left navigation panel)
   - `design-prototype-and-explore-layer-properties-in-the-right-sidebar/` (right properties panel)
   - `explore-design-files/` (spatial layout recap)
   - `adjust-your-zoom-and-view-options/` (header of right panel)
3. **`helper/analysis/ui-map.md`** and **`helper/analysis/panel-states.md`** — already-synthesized UI map and per-panel state rules. Agent B treats these as pre-digested input to avoid re-reading the raw corpus for high-level structure.
4. **`plan/00-overview.md`** — for functional-scope vs visual-scope-only flags (§2 and §3 of that file). Every UI element in Agent B's output must carry the correct flag.
5. **`CLAUDE.md`** — for overall project scope context.

Agent B does **not** read articles outside Figma Design (Dev Mode, Figma Draw, Projects) — those products are out of scope for the mock.

## 3. Output — structure

All outputs land under `extracted/ui-schema/`. One file per UI region plus a few cross-cutting files:

```
extracted/ui-schema/
├── regions/
│   ├── toolbar.md
│   ├── left-navigation.md
│   ├── right-properties.md
│   ├── canvas-overlays.md
│   └── floating-overlays.md
├── chrome.md              ← file-name bar, avatar stack, Share button, top chrome
├── state-matrix.md        ← selection-type → right-panel-sections-shown mapping
├── index.md               ← top-level index with cross-refs and quick lookup
└── gaps.md                ← flagged gaps where extraction could not determine
                             structure / state / appearance from the corpus
```

**Format:** Markdown with embedded structured blocks. Not JSON — easier for me to read and edit, easier for Agent B to produce, and each region's information is heterogeneous enough that JSON rigidity would hurt more than help.

## 4. Output — per-element schema template

Every UI element documented in a region file follows this template:

```
### <element-name>
- **Scope flag:** functional-in-scope | visual-only (per plan/00 §2/§3)
- **Location:** <where in parent region, e.g. "toolbar, group 3, rightmost">
- **Trigger / shortcut:** <if applicable, from docs>
- **Default appearance:** <short descriptive: icon type, chevron yes/no, background>
- **States:**
  - default — <description>
  - hover — <description or "not covered in corpus">
  - active / selected — <description>
  - disabled — <description or "N/A">
  - <other context-dependent variants>
- **State-driven content changes:** <when selecting X vs Y, does this element change?>
- **Reference images:**
  - `<path/to/image.png>` — <what this image shows>
  - `<path/to/image.png>` — <what this image shows>
- **Source articles:** <article slugs>
- **Notes / gaps:** <anything worth flagging>
```

The template is intentionally loose. Not every field applies to every element; fields that do not apply are omitted, not left blank.

## 5. Regions to cover (closed list)

Agent B must produce one regions/ file per entry below. No new region files outside this list.

| File | Covers |
|---|---|
| `regions/toolbar.md` | Bottom-center floating toolbar: Move/Hand/Scale dropdown, Region tools dropdown (Frame/Section/Slice), Shape tools dropdown (Rect/Line/Arrow/Ellipse/Polygon/Star/Image-video), Creation tools dropdown (Pen/Pencil), Text, Comment dropdown (Comment/Annotation/Measurement), Actions menu, Mode switcher (Design/Prototype/Dev Mode), Draw toggle. Plus secondary toolbar variants (vector edit, Dev Mode, Draw) — **mark as visual-only / out-of-scope flag**. |
| `regions/left-navigation.md` | Left nav panel: file-name dropdown + main `…` menu, minimize-UI button, tabs (File / Assets), pages selector, layers tree, Find/Replace takeover, Assets tab body. Rolling-out narrow left navigation bar (variables / assets / find+replace shortcuts, file notifications) — **mark visual-only if it exists in the corpus imagery**. |
| `regions/right-properties.md` | Right panel: header row (zoom % + view options dropdown), sub-header (Mask / Component / Boolean / More), tabs (Design / Prototype), Design-tab sections (Layout, Position, Appearance, Typography, Fill, Stroke, Effects, Component, Export). Per-section: headers, inputs, swatches, toggles, overflow `+` / `…` / `>` buttons. No-selection state (Page section + local styles + Export page). |
| `regions/canvas-overlays.md` | On-canvas chrome: selection bounding box + W×H label, rotation cursor, corner handles, corner-radius circle handles, smart-selection pink handles, arc handles on ellipses, dashed selection bounds for parent, layout guides, snap / measure guides, pixel grid, action bar (bottom-center on canvas: "Mark as ready for dev" — **visual-only** — create-component — **visual-only**), multiplayer cursors — **visual-only**. |
| `regions/floating-overlays.md` | Non-docked surfaces: color picker, dropdowns anchored to buttons, right-click context menu, rename modal (`Cmd/Ctrl R`), bulk export modal — **visual-only** — toast notifications, keyboard shortcuts panel, help & resources. |
| `chrome.md` | Top chrome: file-name bar (when it sits outside the left nav), avatar stack, Share button, branch indicator — **visual-only**. |
| `state-matrix.md` | A table: selection type (nothing / single shape / multi shape / frame / text / image / group / mixed / auto-layout frame — **visual-only** — component instance — **visual-only**) → which right-panel sections are shown / hidden / modified. Uses the same rules already captured in `helper/analysis/panel-states.md` but re-expressed as a lookup table keyed on selection type. |
| `index.md` | Top-level table of contents with links and a one-line summary of each region file. Also includes a scope-flag summary (how many elements are functional-in-scope vs visual-only per region). |
| `gaps.md` | A flat list of flagged gaps. Each entry: what is missing, why it matters, which region file referenced it, what would close the gap (typically: "user provides screenshot of X state"). |

## 6. Image handling

- **Image role in the schema:** reference only. Each state of each element should point to at least one image if the corpus contains one. Image paths are relative to repo root, e.g. `helper/figma_docs/articles/Figma Design/navigating-ui3/images/img_01.png`.
- **Description of appearance:** short, descriptive, non-numeric. Examples: "rounded pill shape", "icon + chevron", "blue filled background when active". Not: "32px tall", "#0D99FF fill". Color tokens and exact measurements are out of scope for Agent B — they will be set by me and the user at the render layer.
- **No pixel sampling, no proportional measurement, no hex codes.**
- **Theme:** the corpus is overwhelmingly light-theme. Agent B extracts structure and reference-image pointers against the light-theme imagery as it appears. Dark theme is handled later at the render layer through a `ThemeProvider` + color tokens; Agent B does not need to produce dark-theme descriptions.
- **UI3 vs pre-UI3 filter:** some older articles may still have pre-UI3 screenshots. Agent B must prefer images consistent with `navigating-ui3/` and `access-design-tools-from-the-toolbar/`. If an article's images look pre-UI3 (top toolbar with icons along the top, different panel chrome), Agent B flags the mismatch in the relevant region file's notes, does not use those images as reference.

## 7. Gap handling

- Every time Agent B cannot determine a state, a variant, or an element's appearance from the corpus, it writes an entry into `gaps.md` and references the gap in the region file where it applies.
- Agent B **does not invent**. An unknown state is written as `state: <not covered in corpus>` and listed in `gaps.md`.
- Gaps are intentionally fine-grained. "Hover state of the shape tools dropdown button" is a gap. "Full toolbar" is not a gap.
- Every gap entry in `gaps.md` should include: region, element, what's missing, suggested resolution (usually: "user provides screenshot of X with Y selected").

## 8. Quality gates

Agent B's output passes only if:

1. Every file listed in §5 exists.
2. Every region file documents at least one UI element, and every documented element has a scope flag, default appearance, and at least one reference image OR an explicit gap entry.
3. Every visual-only element is consistent with `plan/00 §3` — no element is labeled functional-in-scope that isn't in `plan/00 §2`, and no element is labeled visual-only that is in `plan/00 §2`.
4. `state-matrix.md` covers every selection type listed in §5 and references `helper/analysis/panel-states.md` consistently (no contradictions).
5. `gaps.md` is present (may be empty if no gaps; gaps are welcome — silent invention is not).
6. `index.md` summarizes scope-flag counts per region.

Gates are verified by me (primary agent) reading the output after Agent B finishes, against these criteria, before we move to Phase 3.

## 9. Batching strategy

Agent B runs in one pass over the full region list in §5. Rationale:

- The output files are independent from one another once the regions are fixed (which they are, in §5's closed list).
- Single-pass minimizes coordination overhead and avoids Agent B re-reading context across multiple invocations.
- Single-pass is safe only because Agent B does not write code. If the output is wrong, we re-run; no code needs rollback.

If a single pass blows through available context or produces degraded output near the end, fallback is region-by-region: `toolbar.md` first, then `right-properties.md` (largest), then `left-navigation.md`, `canvas-overlays.md`, `floating-overlays.md`, `chrome.md`, `state-matrix.md`, `index.md`, `gaps.md`.

## 10. Agent brief structure

When dispatching Agent B, the prompt includes:

1. **Role statement** — "You are a UI schema researcher. You do not write code."
2. **Task** — "Produce the files listed in §5 of `plan/01-ui-schema-extraction.md` under `extracted/ui-schema/`."
3. **Inputs** — the list in §2, with explicit paths.
4. **Output template** — §4 verbatim.
5. **Scope filter** — `plan/00 §2` and `§3` verbatim. Every element must be flagged accordingly.
6. **Image handling rules** — §6 verbatim. No pixel math, no hex codes.
7. **Gap handling rules** — §7 verbatim. No invention.
8. **Quality checklist** — §8 verbatim. Agent B self-checks before finishing.
9. **UI3-vs-pre-UI3 filter** — concrete phrasing for how to detect and skip pre-UI3 screenshots.
10. **Stop condition** — "When all files in §5 exist and pass the §8 checklist, output a completion summary and stop."

The full agent prompt will be assembled at dispatch time. The pieces above are the ingredients; this doc is the recipe.

## 11. Risks and known limits

- **Image reading accuracy is variable.** Agent B's descriptions of icon shapes or panel structure may be wrong in edge cases. Mitigation: I spot-check by opening the referenced images myself for 2–3 randomly-chosen elements per region file.
- **Pre-UI3 contamination.** Older articles may still reference old chrome. Mitigation: §6's UI3-vs-pre-UI3 filter + `gaps.md` flagging when mixed.
- **Coverage gaps (entire states missing from corpus).** Expected and handled via `gaps.md`. User fills gaps with ad-hoc screenshots later, not now.
- **Scope-flag errors** (marking visual-only as functional or vice versa) are corrected by me in review against `plan/00 §2/§3` before we move on.
- **Corpus drift over time** is not a concern — the corpus is static in this repo.
- **Hover / focus / disabled states** are often not photographed in marketing-grade help content. Most such states will land in `gaps.md`. That is fine; we fill them as the build progresses.

## 12. Decisions required before dispatching Agent B

- ✅ **Theme**: dark as default, light+dark tokens via `ThemeProvider`. Agent B extracts structure against light-theme imagery (the corpus's majority). Dark token values are filled by user at the render layer, separately.
- ✅ **Output format**: markdown with structured blocks per element.
- ✅ **Batching**: single-pass, with region-by-region fallback if quality degrades.
- ✅ **Scope filter source**: `plan/00 §2` and `§3`.
- Open: none at dispatch time.

## 13. When Agent B is dispatched

- After `plan/00`, `plan/01` are both approved.
- `plan/02` (feature research) can be written in parallel with Agent B running — it does not depend on `extracted/ui-schema/` content.
- `plan/03` (engine architecture) benefits from Agent B's output being available (state-matrix informs engine state model), so we aim to have `extracted/ui-schema/` produced before writing `plan/03`.

## 14. Exit criteria for this plan

This plan document is done when:

- User approves it as-is or with edits applied.
- All decisions in §12 are marked ✅.
- Agent B's brief template (§10) is reviewable as a standalone prompt a human or another agent could execute.
