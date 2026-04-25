# Use slice tool

- **Category:** region-tools
- **One-line summary:** Define a rectangular export region on the canvas via the Slice tool.

## Triggers
- Toolbar: Region-tools dropdown → Slice. No default keyboard shortcut in UI3.

## Preconditions
- Tool set to Slice.
- Pointer over canvas.

## Inputs
- Pointer-down + pointer-move + pointer-up.

## Behavior
1. Tool activation: crosshair.
2. Pointer-down + drag: live-preview slice bounds (dashed outline distinct from regular shapes).
3. Pointer-up: create a slice layer with `x/y/w/h`.
4. Selection = new slice.
5. Slice can be moved / resized like any layer; it appears in Layers panel with a slice icon.

## Outputs
- **Scene graph changes:** one new slice layer.
  - `type: "slice"`
  - `x`, `y`, `w`, `h`.
  - No fill, no stroke — purely an export region.
- **Selection changes:** selection = new slice.

## UI feedback
- Crosshair during placement.
- Slice renders as a dashed outline on canvas (not a visible filled rectangle).
- New layer in Layers panel with slice icon.
- Right panel: Position (X/Y/W/H) + Export section. **Export is visual-only** per `plan/00 §3` — the slice itself is functional (creates a region) but the export operation on it is a no-op.

## Side effects
- Undo stack: adds "create slice" entry.

## Related UI schema entries
- `regions/toolbar.md` → region-tools-dropdown (Slice entry)
- `regions/right-properties.md` → export-section (visual-only)

## Semantic event(s) candidate
- `create_slice { x, y, w, h, parent_id | null, trigger: "toolbar" }`

## Source articles
- `access-design-tools-from-the-toolbar`
- `export-from-figma-design`
- workflow reference in `workflows.md`: "Slice-based region export"

## Notes / gaps
- Slice tool is coupled to export. Export out of functional scope in our mock, so creating a slice is functional but the Export button on the right panel does nothing. Distinct from being entirely visual-only: user can place + resize slices, they render, they persist in the scene graph.
- Slice ordering in Layers panel (above all content vs interleaved) not documented precisely; treat as a regular layer at its natural z-order.
