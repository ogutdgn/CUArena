# Set stroke

- **Category:** properties
- **One-line summary:** Add, remove, or change stroke properties — color, weight, alignment, dash — on selected layer(s).

## Triggers
- Right-sidebar Stroke section:
  - `+` → add a new stroke
  - Swatch → color picker (same flow as fill)
  - Weight input → change stroke weight
  - Alignment picker (Inside / Center / Outside)
  - Hex / opacity / eye / `…` (same per-row controls as Fill)
  - Advanced popover (dashed / cap / join / end-points) — mixed scope

## Preconditions
- Selection is non-empty.
- Selected layer type supports strokes.

## Inputs
- User interaction with the Stroke section controls.

## Behavior

Analogous to Fill: add / remove / reorder / toggle-visible / change color / change opacity.

Stroke-specific:
- **Weight:** type or drag; applies to all selected layers' outermost stroke.
- **Alignment:** three-state (Inside / Center / Outside); affects how stroke width renders relative to path.
- **Dash pattern:** opens advanced popover with dash / gap inputs.
- **End caps / joins:** `visual-only` for advanced cap / join types; default (butt / miter) used.

## Outputs
- **Scene graph changes:** selected layers' `strokes` array and stroke attributes mutated.
- **Selection changes:** none.

## UI feedback
- Canvas: stroke updates live.
- Panel: section values update.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → stroke-section
- `regions/floating-overlays.md` → color-picker

## Semantic event(s) candidate
- `set_stroke_color { layer_ids, stroke_index, from, to, trigger }`
- `set_stroke_weight { layer_ids, from, to, trigger: "input" | "scrub" }`
- `set_stroke_alignment { layer_ids, to: "inside" | "center" | "outside", trigger }`
- `add_stroke { layer_ids, stroke_index, trigger: "panel_plus" }`
- `remove_stroke { layer_ids, stroke_index, trigger }`
- `set_stroke_dash { layer_ids, dash: [n, m], trigger }`

## Source articles
- `apply-and-adjust-stroke-properties`
- `convert-strokes-to-vector-paths`

## Notes / gaps
- Gradient / Pattern / Image strokes: treat as `visual-only` (plan/00 §3 — gradient fills out of scope implies gradient strokes out of scope).
- Advanced popover's outline-stroke / variable-width-profile controls are `visual-only` (vector-network advanced features; not in plan/00 §2 explicitly).
