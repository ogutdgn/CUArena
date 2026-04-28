# UI Schema Index

**Purpose:** Top-level table of contents for `extracted/ui-schema/`. One-line summary per file + scope-flag counts per region.

This schema catalogs the Figma Design UI3 chrome. Descriptions are qualitative (shape, icon, layout) — not numeric (no pixel measurements, no hex codes). Color + spacing values are handled at render time via a ThemeProvider.

**Scope flag legend:**
- `functional-in-scope` — the element represents a feature in `plan/00 §2`; clicking it does something
- `visual-only` — the element is rendered (UI fidelity requires it) but clicking is a no-op; feature is in `plan/00 §3`
- `not rendered` — not even displayed (plan/00 §3a: Dev Mode overlays, Prototype overlays, Draw mode variants, etc.)

---

## Files

| File | One-line summary |
|---|---|
| [`regions/toolbar.md`](regions/toolbar.md) | Bottom-center floating toolbar — tool selection + mode switcher |
| [`regions/left-navigation.md`](regions/left-navigation.md) | Left sidebar — file metadata, pages, layers tree, Assets tab |
| [`regions/right-properties.md`](regions/right-properties.md) | Right sidebar — selection-driven property sections, Design / Prototype tabs |
| [`regions/canvas-overlays.md`](regions/canvas-overlays.md) | On-canvas chrome — selection handles, guides, action bar |
| [`regions/floating-overlays.md`](regions/floating-overlays.md) | Non-docked surfaces — color picker, context menu, modals, toasts |
| [`regions/color-picker.md`](regions/color-picker.md) | **(deep)** Color picker overlay — fill type, blend mode, contrast, SV square, hue/opacity sliders, color models, document/library colors, gradient stops, image controls |
| [`regions/context-menu.md`](regions/context-menu.md) | **(deep)** Right-click menu inventory per selection / context |
| [`chrome.md`](chrome.md) | Top-level chrome — avatar stack, Share, branch indicator (mostly inside right-panel header in UI3) |
| [`state-matrix.md`](state-matrix.md) | Selection type × right-panel sections lookup table |
| [`unsupported-toast.md`](unsupported-toast.md) | Mock-specific fallback toast for `visual-only` clicks |
| [`panel-scroll-behavior.md`](panel-scroll-behavior.md) | Cross-region scroll behavior for left/right panels + overlays |
| [`gaps.md`](gaps.md) | Flagged gaps where corpus could not cover a state; resolution hints |

---

## Scope-flag counts per region

Approximate counts (an element with sub-buttons or dropdown entries is counted once at the top level; sub-entries summarized in the region file itself).

| Region | Elements | Functional-in-scope | Visual-only | Not rendered / view-only |
|---|---|---|---|---|
| Toolbar | 9 top-level (6 dropdowns + 3 single buttons + mode switcher) | ~5 (Move tools, Region tools, Shape tools, Creation tools, Text) | ~3 (Comment dropdown, Actions menu, Draw / Dev Mode segments of switcher) | ~1 (Ask-to-edit variant) |
| Left navigation | 8 top-level | ~5 (Minimize UI, File tab, Pages selector, Layers tree, Collapse-layers) | ~3 (File-name dropdown entries, Main menu, Assets tab body, Find-replace takeover, new nav bar) | 0 |
| Right properties | ~15 sections + header | Page, Position, Layout (W/H/Clip), Appearance (core), Typography, Fill, Stroke, Effects, (Export rendered as visual-only) | Zoom-view-options (most entries), Sub-header (Mask/Component/Boolean), Prototype tab body, Export section, Component section, Auto layout, some Appearance sub-controls | Comment / Properties tabs (view-only) |
| Canvas overlays | ~15 | Selection box, W×H label, handles, corner-radius handles, arc handles, dashed parent bounds, snap/measure guides, insertion crosshair, marquee box, rotation cursor, pan/zoom | Action bar, pixel grid, multiplayer cursors, mask outlines, layout guides, smart-selection pink handles | Dev Mode / Prototype overlays |
| Floating overlays | ~15 | Color picker (core), rename modal | Dropdowns (mostly), right-click context menu (mixed), bulk-export modal, toasts (render), keyboard shortcuts, help & resources, actions panel, libraries modal, share modal, advanced export, page context menu | Variables modal, interaction-details modal, compare-changes modal, component-playground, inline preview, presentation view, spotlight, branches modal, version history, check-designs |
| Chrome | 5 | File-name bar (content) | Avatar stack, Share, Present triangle, branch indicator | View-only "Ask to edit", Comment / Properties tabs |

---

## How the schema is used downstream

- `plan/02-feature-research.md` → Agent A links every feature's `Related UI schema entries` to entries here.
- `plan/03-engine-architecture.md` → engine / UI component structure is informed by the region files + state-matrix.
- `plan/04-build-phases.md` → each build slice renders the relevant region + canvas affordances from this schema.

## Known limits

- Descriptions are qualitative, not pixel-accurate. Final spacings / colors / font metrics live in the render layer (ThemeProvider + CSS variables).
- The corpus is overwhelmingly light-theme; dark-theme colors are deferred to the ThemeProvider.
- Every flagged gap is listed in `gaps.md`. Most gaps close at build time via user-provided screenshots or reasonable defaults.

## Source summary

Primary sources consulted for this schema:

- `helper/analysis/ui-map.md` — canonical spatial layout
- `helper/analysis/panel-states.md` — authoritative per-panel state rules
- `helper/figma_docs/articles/Figma Design/navigating-ui3/` — UI3 overview (54 images, most comprehensive visual reference)
- `helper/figma_docs/articles/Figma Design/access-design-tools-from-the-toolbar/` — toolbar reference
- `helper/figma_docs/articles/Figma Design/view-layers-and-pages-in-the-left-sidebar/` — left panel reference
- `helper/figma_docs/articles/Figma Design/design-prototype-and-explore-layer-properties-in-the-right-sidebar/` — right panel reference
- Feature-specific articles referenced per element in region files.

Products **not** consulted (out of mock scope): Dev Mode, Figma Draw, Projects tutorials.
