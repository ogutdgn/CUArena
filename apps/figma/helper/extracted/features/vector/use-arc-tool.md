# Use arc tool (arcs / semi-circles / rings)

- **Category:** vector
- **One-line summary:** Convert an ellipse into an arc, pie, or ring by adjusting its arc-handles on the canvas.

## Triggers
- Select an ellipse layer → on-canvas arc handles appear (small handles next to the ellipse).
- Drag the arc handles to set start angle, end angle, and inner radius (for ring).

## Preconditions
- Selected layer is an ellipse.

## Inputs
- Pointer drag on arc handles.

## Behavior
1. **Sweep angle handle** — drags arc-shape into a pie / wedge.
2. **Start angle handle** — sets where the arc begins.
3. **Inner radius handle** — converts the arc into a ring (donut) when dragged inward.
4. Right sidebar exposes numeric inputs for these properties (start, sweep, inner radius).

## Outputs
- **Scene graph changes:** ellipse layer gains arc properties: `arc_start`, `arc_sweep`, `arc_inner_radius_ratio`.
- **Selection changes:** none.

## UI feedback
- Arc handles render when ellipse selected.
- Right sidebar shows arc fields under the shape's properties.

## Side effects
- Undo stack: per-action entries.

## Related UI schema entries
- `regions/canvas-overlays.md` → arc-handles
- `regions/right-properties.md` → arc-properties (start, sweep, inner)

## Semantic event(s) candidate
- `set_arc_properties { layer_id, property: "start" | "sweep" | "inner_radius_ratio", from, to, trigger: "canvas_handle_drag" | "panel_input" }`

## Source articles
- `arc-tool-create-arcs-semi-circles-and-rings`

## Notes / gaps
- Real Figma's arc-handles are intrinsic to the ellipse shape, not a separate tool — the article frames this as the "arc tool" concept.
