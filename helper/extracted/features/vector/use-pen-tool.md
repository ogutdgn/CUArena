# Use Pen tool (create vector network)

- **Category:** vector
- **One-line summary:** Build a vector network — anchor points + optional bezier handles — by clicking and click-dragging with the Pen tool.

## Triggers
- Keyboard: `P` — activates Pen tool.
- Toolbar: Creation-tools dropdown → Pen.

## Preconditions
- Tool set to Pen.
- Pointer over canvas.

## Inputs
- Sequence of pointer interactions:
  - Click → add corner point (no handles).
  - Click-drag → add point with symmetric bezier handles dragging out from the anchor.
  - Click an existing point in the current network → close the path at that point.
  - Esc / Enter → finish without closing.
- Modifiers:
  - `Shift` — constrain segment angle to 0° / 15° / etc.
  - `Alt/Option` — break handle symmetry when dragging (one side only).

## Behavior
1. Tool activation: crosshair cursor with a pen-icon glyph.
2. First click: start a new vector layer at that point; the new layer is immediately selected and in an implicit creation-edit mode.
3. Each subsequent click / click-drag: appends a new point connected by a straight (click) or curved (click-drag) segment.
4. Hovering over the first point shows a small close-path indicator (circle); clicking there closes the path.
5. Pressing Enter / Esc finishes without closing; path remains open.

## Outputs
- **Scene graph changes:** creation starts a vector layer on first click. Subsequent clicks extend the same layer.
  - `type: "vector"`
  - `points: [...]` (sequence of anchor points, each with optional `handleIn` and `handleOut`)
  - `closed: boolean`
  - `stroke: [{ type: "solid", color: default, weight: 1 }]`
  - `fill: []` (Figma default; closing may auto-add fill — engine decision)
- **Selection changes:** selection = new vector layer throughout creation.
- **Mode state change:** enters an implicit "pen creation" mode for the duration of the path; exits on finish (Enter / Esc / close).

## UI feedback
- Crosshair + pen glyph cursor.
- Live rubber-band segment from last-placed point to pointer.
- Anchor points rendered as small squares; handles rendered as thin lines with round endpoints.
- Hovering over start point shows close-path indicator.

## Side effects
- Undo stack: coalesced — typically one entry per completed path (from first click to finish). `plan/03` may refine (per-point undo during creation).

## Related UI schema entries
- `regions/toolbar.md` → creation-tools-dropdown (Pen)
- `regions/canvas-overlays.md` → insertion-crosshair

## Semantic event(s) candidate
- `create_vector_with_pen { layer_id, points: [...], closed, trigger: "shortcut_P" | "toolbar" }`
- Sub-events during creation may also emit: `pen_add_point { layer_id, point, handle_in, handle_out }`.
- `plan/03` consolidates.

## Source articles
- `vector-networks`
- `edit-vector-layers`
- `access-design-tools-from-the-toolbar`

## Notes / gaps
- "Vector network" (Figma's term) differs from SVG path: a single network can branch (points shared between multiple segments). Engine model must support this for fidelity, but basic linear paths are the most common case.
- Default fill on close: some contexts auto-add a black fill when a path closes. Confirm at build time.
