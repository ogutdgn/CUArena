# 01 — UI Schema Reference

> **Status:** ✅ Extraction completed. Agent B's output landed in `helper/extracted/ui-schema/` and was subsequently extended with deeper region docs (color-picker, context-menu, panel-scroll-behavior, unsupported-toast). The current contents of `helper/extracted/ui-schema/` are the post-extension version. This doc describes what's there, how it was produced, and how to use it.

> **How to use this doc:** when you need to render or fix a UI element, jump to **Workflow 2 — Adding a UI element** in `helper/00-overview.md §7a` for the recipe. Come back here for the regions inventory in §3 and §5. Don't read top-to-bottom unless you're onboarding.

> **Pointers from this doc into the corpus:**
> - **Output location:** `helper/extracted/ui-schema/`
> - **Source articles for UI regions:** `helper/figma_docs/articles/Figma Design/{navigating-ui3, access-design-tools-from-the-toolbar, view-layers-and-pages-in-the-left-sidebar, design-prototype-and-explore-layer-properties-in-the-right-sidebar, explore-design-files, adjust-your-zoom-and-view-options}/`
> - **Companion analysis docs:** `helper/analysis/ui-map.md` (spatial layout), `helper/analysis/panel-states.md` (per-panel state rules)
> - **State matrix authority:** `helper/extracted/ui-schema/state-matrix.md`

## 1. Purpose

Agent B read the Figma documentation corpus (`helper/figma_docs/` articles + images) and produced a structured UI schema under `helper/extracted/ui-schema/`. The schema tells the build phase *what UI elements exist*, *where they live*, *what states they have*, and *which reference image shows each state*.

Agent B did **not** write code, did **not** extract pixel measurements, did **not** sample hex color codes, did **not** produce mockups. It cataloged and cross-referenced.

## 2. Inputs (historical)

Agent B read from (in priority order):

1. **`helper/figma_docs/articles/Figma Design/`** — all 175 Figma Design articles. Each article has `content.md`, `metadata.json`, and an `images/` folder.
2. **UI-focused articles to read first** (highest reference density):
   - `navigating-ui3/` (54 images — canonical UI3 overview)
   - `access-design-tools-from-the-toolbar/` (toolbar)
   - `view-layers-and-pages-in-the-left-sidebar/` (left navigation panel)
   - `design-prototype-and-explore-layer-properties-in-the-right-sidebar/` (right properties panel)
   - `explore-design-files/` (spatial layout recap)
   - `adjust-your-zoom-and-view-options/` (header of right panel)
3. **`helper/analysis/ui-map.md`** and **`helper/analysis/panel-states.md`** — already-synthesized UI map and per-panel state rules. Treated as pre-digested input.
4. **`plan/00-overview.md`** — for functional-scope vs visual-scope-only flags. Every UI element in Agent B's output carries the correct flag.
5. **`CLAUDE.md`** — for overall project scope context.

> **Note:** at the time of the original run, `feature-inventory.md` (broad/shallow, 4-product) also existed as input; that file has since been deleted in favor of the deeper `feature-inventory-deep.md`. This change does not invalidate Agent B's output (Agent B never used `feature-inventory.md` as a hard input — it was Agent A's primary feature catalog).

Agent B did **not** read articles outside Figma Design (Dev Mode, Figma Draw, Projects).

## 3. Output — actual structure

```
helper/extracted/ui-schema/
├── regions/
│   ├── toolbar.md                 ← Agent B
│   ├── left-navigation.md         ← Agent B
│   ├── right-properties.md        ← Agent B
│   ├── canvas-overlays.md         ← Agent B
│   ├── floating-overlays.md       ← Agent B
│   ├── color-picker.md            ← post-extension (deeper picker spec)
│   └── context-menu.md            ← post-extension (per-context right-click inventory)
├── chrome.md                      ← Agent B (file-name bar, avatar stack, Share, branch indicator)
├── state-matrix.md                ← Agent B (selection-type → right-panel-sections lookup)
├── unsupported-toast.md           ← post-extension (mock-specific fallback toast spec)
├── panel-scroll-behavior.md       ← post-extension (cross-region scroll behavior)
├── index.md                       ← top-level index
└── gaps.md                        ← flagged extraction gaps
```

**Format:** Markdown with embedded structured blocks per element.

## 4. Output — per-element schema template

Every UI element documented in a region file follows this template:

```
### <element-name>
- **Scope flag:** functional-in-scope | visual-only (per plan/00 §2/§3)
- **Location:** <where in parent region>
- **Trigger / shortcut:** <if applicable, from docs>
- **Default appearance:** <short descriptive: icon type, chevron, background>
- **States:**
  - default — <description>
  - hover — <description or "not covered in corpus">
  - active / selected — <description>
  - disabled — <description or "N/A">
  - <other context-dependent variants>
- **State-driven content changes:** <when selecting X vs Y, does this element change?>
- **Reference images:**
  - `<path/to/image.png>` — <what this image shows>
- **Source articles:** <article slugs>
- **Notes / gaps:** <anything worth flagging>
```

The template is intentionally loose. Fields that do not apply are omitted, not blank.

## 5. Regions covered (final)

| File | Covers | Origin |
|---|---|---|
| `regions/toolbar.md` | Bottom-center floating toolbar; vector-edit secondary toolbar; Dev Mode / Draw variants flagged visual-only. | Agent B |
| `regions/left-navigation.md` | Left nav panel: file-name dropdown, minimize-UI, tabs (File / Assets), pages selector, layers tree, Find/Replace takeover. Rolling-out narrow left navigation bar flagged visual-only. | Agent B |
| `regions/right-properties.md` | Right panel: header row, sub-header, tabs, Design-tab sections (Layout, Position, Appearance, Typography, Fill, Stroke, Effects, Component, Export). No-selection state. | Agent B |
| `regions/canvas-overlays.md` | On-canvas chrome: selection bbox, handles, rotation cursor, snap/measure guides, layout guides, action bar, multiplayer cursors, parent-bounds dashed overlay. | Agent B |
| `regions/floating-overlays.md` | Color picker (high-level), dropdowns, context menu (high-level), rename modal, bulk export modal, toasts, keyboard-shortcuts panel, help & resources. | Agent B |
| `regions/color-picker.md` | **Deep**: 14 sub-sections of the color picker — fill type, blend mode, contrast checker, SV square, eyedropper, hue/opacity sliders, color models, channel inputs, document/library colors, gradient stops, image controls, pattern controls. | post-extension |
| `regions/context-menu.md` | **Deep**: right-click menu inventory per selection / context — empty canvas, single layer, multi-select, frame, component, boolean group, vector layer, vector edit, panel rows, page rows, comment pin, text-edit. | post-extension |
| `chrome.md` | File-name bar, avatar stack, Share button, branch indicator. | Agent B |
| `state-matrix.md` | Selection type × right-panel sections lookup. | Agent B |
| `unsupported-toast.md` | Mock-specific fallback toast for visual-only clicks; element registry mapping. | post-extension |
| `panel-scroll-behavior.md` | Cross-region scroll behavior for left/right panels + overlays. | post-extension |
| `index.md` | Top-level table of contents with cross-refs and quick lookup. | Agent B + updated post-extension |
| `gaps.md` | Flagged gaps from extraction with resolution hints. | Agent B |

## 6. Image handling

- **Image role in the schema:** reference only. Each state of each element points to at least one image if the corpus contains one. Image paths are relative to repo root.
- **Description of appearance:** short, descriptive, non-numeric. No pixel sampling, no proportional measurement, no hex codes.
- **Theme:** the corpus is overwhelmingly light-theme. Agent B extracted structure against the light-theme imagery; dark theme is handled later at the render layer through a `ThemeProvider` + color tokens.
- **UI3 vs pre-UI3 filter:** prefer images consistent with `navigating-ui3/` and `access-design-tools-from-the-toolbar/`. Pre-UI3 screenshots flagged.

## 7. Gap handling

- Every state Agent B couldn't determine was written into `gaps.md` and referenced in the relevant region file.
- **Agent B does not invent.** Unknown states written as `state: <not covered in corpus>` and listed in `gaps.md`.
- Gaps fine-grained: "Hover state of the shape tools dropdown button" is a gap; "Full toolbar" is not.
- Gap entries include: region, element, what's missing, suggested resolution.

## 8. Quality gates (verified at completion)

Agent B's output passed only if:

1. ✅ Every file listed in §5 exists.
2. ✅ Every region file documents at least one UI element with a scope flag, default appearance, and at least one reference image OR an explicit gap entry.
3. ✅ Every visual-only element is consistent with `plan/00 §3`.
4. ✅ `state-matrix.md` covers every selection type listed and references `helper/analysis/panel-states.md` consistently.
5. ✅ `gaps.md` is present.
6. ✅ `index.md` summarizes scope-flag counts per region.

## 9. Batching strategy (executed)

Agent B ran in a single pass over the full region list. Outputs are independent once regions are fixed; single-pass minimized coordination overhead. No region-by-region fallback was needed.

## 10. Agent brief (historical reference)

When dispatching Agent B, the prompt included:

1. Role statement — "You are a UI schema researcher. You do not write code."
2. Task — produce the files listed in §5 under `helper/extracted/ui-schema/`.
3. Inputs — the list in §2, with explicit paths.
4. Output template — §4 verbatim.
5. Scope filter — `plan/00 §2` and `§3` verbatim.
6. Image handling rules — §6 verbatim. No pixel math, no hex codes.
7. Gap handling rules — §7 verbatim. No invention.
8. Quality checklist — §8 verbatim.
9. UI3-vs-pre-UI3 filter.
10. Stop condition — "When all files in §5 exist and pass §8 checklist, output a completion summary and stop."

## 11. Risks and known limits (post-mortem)

- **Image reading accuracy** — Agent B's descriptions of icon shapes were spot-checked.
- **Pre-UI3 contamination** — caught and flagged via `gaps.md`.
- **Coverage gaps** — listed in `gaps.md`. User fills with ad-hoc screenshots when implementation reveals a need.
- **Scope-flag errors** — corrected against `plan/00 §2/§3` in review.
- **Hover / focus / disabled states** are often not photographed in marketing-grade help content. Most landed in `gaps.md`. That is fine; we fill them as the build progresses.

## 12. Decisions (resolved)

- ✅ **Theme**: dark as default, light+dark tokens via `ThemeProvider`. Agent B extracted structure against light-theme imagery.
- ✅ **Output format**: markdown with structured blocks per element.
- ✅ **Batching**: single-pass.
- ✅ **Scope filter source**: `plan/00 §2` and `§3`.

## 13. Dispatch + completion

- Agent B was dispatched after `plan/00` and `plan/01` were approved.
- `plan/02` (feature research) was written in parallel; Agent A ran after Agent B finished so that `Related UI schema entries` cross-references were filled.
- Post-extraction extension (color-picker.md, context-menu.md, unsupported-toast.md, panel-scroll-behavior.md) was added when the feature scope expanded — these documents fill regions that needed deeper detail than Agent B's first pass.

## 14. Exit criteria — met

- ✅ User approved.
- ✅ All decisions in §12 marked ✅.
- ✅ Agent B's brief was reviewable as a standalone prompt.
- ✅ Output produced and extended.
