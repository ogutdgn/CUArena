# Selection → Right-Panel State Matrix

**Purpose:** Authoritative lookup of which right-panel sections appear, in what order, for each selection type. Synthesized from `helper/analysis/panel-states.md` and the canonical sidebar article.

**Legend:**
- ✓ = section present and functional
- ○ = section present but visual-only (rendered, controls inert)
- — = section absent
- *context visual-only* = the entire selection type is a visual-only context; noted for completeness, never entered in our mock

---

## Master matrix

| Selection type | Sub-header (Mask / Component / Boolean / More) | Page | Local styles+variables | Export page | Alignment row | Position | Layout | Auto layout | Appearance | Typography | Fill | Stroke | Effects | Component | Export | Selection colors |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Nothing selected** | ○ | ✓ | ○ | ○ | — | — | — | — | — | — | — | — | — | — | — | — |
| **Single shape** (rect / ellipse / polygon / star / line / arrow) | ○ | — | — | — | ✓ | ✓ | ✓ (W/H only) | — | ✓ | — | ✓ | ✓ | ✓ | — | ○ | — |
| **Frame** | ○ | — | — | — | ✓ | ✓ | ✓ (W/H + Clip content + Layout guide) | ○ | ✓ | — | ✓ | ✓ | ✓ | — | ○ | — |
| **Section** | ○ | — | — | — | ✓ | ✓ | ✓ (W/H, minimal) | — | ✓ | — | — | — | — | — | ○ | — |
| **Text** | ○ | — | — | — | ✓ | ✓ | ✓ (W/H + text-resizing modes) | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ○ | — |
| **Image layer** | ○ | — | — | — | ✓ | ✓ | ✓ | — | ✓ | — | ✓ (image fill controls) | ✓ | ✓ | — | ○ | — |
| **Group** | ○ | — | — | — | ✓ | ✓ | ✓ (W/H) | — | ✓ | — | — | — | ✓ | — | ○ | — |
| **Vector (from pen / pencil)** | ○ | — | — | — | ✓ | ✓ | ✓ (W/H) | — | ✓ | — | ✓ | ✓ | ✓ | — | ○ | — |
| **Multi-mixed selection** | ○ | — | — | — | ✓ | ✓ | ✓ (W/H, some inputs may read "mixed") | — | ✓ | — | ✓ (if all have fill) | ✓ (if all have stroke) | ✓ | — | ○ | ✓ (when fills differ) |
| **Auto-layout frame** (context visual-only) | ○ | — | — | — | ✓ | ✓ | — | ○ | ✓ | — | ✓ | ✓ | ✓ | — | ○ | — |
| **Component / instance** (context visual-only) | ○ | — | — | — | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ○ | ○ | — |

---

## Notes per section

### Sub-header (Mask / Create component / Boolean / More)
- Always rendered when selection is non-empty. Individual buttons are all visual-only except `More …` which may host a mix (copy props / rename / lock / delete are functional; most other `…` entries visual-only). See `regions/right-properties.md` → sub-header row.
- When selection is empty, the sub-header is absent.

### Page
- Only when selection is empty. Shows background color + hex + hide-in-exports eye.

### Local styles + variables
- Only when selection is empty. Visual-only — we render an empty-state rather than real style / variable lists.

### Export page
- Only when selection is empty. Visual-only.

### Alignment row
- Present whenever 1+ selected. Icons: align left / center-X / right / top / middle-Y / bottom. When multi-selected, distribute horizontal / vertical icons also appear. "Tidy up" (smart-selection) icon appears only when a smart-selection-eligible arrangement is detected — visual-only.

### Position
- X / Y inputs for position. Rotation input. Flip horizontal / flip vertical icons. Constraints icon (appears next to X/Y when the selection is inside a non-auto-layout frame as a child). Ignore-auto-layout icon appears only when a child of an auto-layout frame is selected (visual-only context for us).

### Layout
- Header changes to "Auto layout" when auto-layout is applied to a frame (visual-only context). Otherwise:
  - W / H inputs
  - Lock-aspect toggle
  - Resizing per-axis (Fixed / Hug / Fill / Scale) — Fixed is functional; Hug / Fill / Scale are visual-only (all auto-layout-coupled)
  - Clip content toggle (frames only) — functional
  - Layout guide sub-section (frames only) — visual-only

### Auto layout
- Only appears when a frame has auto layout applied. Contents: flow toggle (vertical / horizontal / grid), padding, gap, 9-position alignment, wrap, resizing, min/max. Entire section visual-only.

### Appearance
- Visibility eye (functional), Blend mode dropdown (visual-only), Variable-mode swatch (visual-only), Opacity input + slider (functional), Corner radius (functional — uniform + independent corners), Corner smoothing (visual-only).

### Typography
- Only appears for text layers / ranges. Controls: text-style picker (visual-only), font family / weight / size / line-height / letter-spacing, horizontal + vertical alignment, `…` opens Type-settings panel (visual-only for advanced tabs).

### Fill
- List of fill rows + `+` add. Each row: swatch (opens color picker), hex, opacity, show-in-exports (visual-only), eye (functional), `…` (mixed).

### Stroke
- List of stroke rows + weight + alignment + advanced settings popover.

### Effects
- List of effect rows. Drop shadow + Layer blur functional; Inner shadow / Background blur / Noise / Texture / Glass visual-only (not in plan/00 §2).

### Component
- Present only for components / instances — visual-only context; never entered in our mock.

### Export
- Present whenever a selection exists; visual-only — Export button is a no-op.

### Selection colors
- Only appears for mixed selections where the fills across the selection are not identical. Controls let you swap / unify the fill across all selected layers. Visual-only (bulk-fill unification is not in plan/00 §2).

### Mask
- Only for mask groups. Visual-only — masks out of scope.

---

## Order of sections in the panel body

For selections, the canonical order (top → bottom) when all applicable sections are present:

1. Sub-header (Mask / Component / Boolean / More)
2. Alignment row
3. Layout (or Auto layout)
4. Position
5. Appearance
6. Typography (only if text)
7. Fill
8. Stroke
9. Effects
10. Component (only if component / instance — visual-only)
11. Export

For no selection:

1. Page
2. Local styles + variables
3. Export page

---

## Edge-state notes

- **Deselect during edit** — right panel reverts to no-selection layout (Page / styles / Export page).
- **Minimize-UI + selection** — right panel temporarily re-expands with only the selection-aware sections until the selection clears.
- **View-only / Dev Mode variants** — not rendered per plan/00 §3a.
- **Multi-edit toggle** — appears in sub-header when applicable (e.g., multi-edit text, multi-edit variants) — visual-only.
