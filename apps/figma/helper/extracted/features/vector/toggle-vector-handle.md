# Toggle vector handle (corner / mirrored / asymmetric)

- **Category:** vector
- **One-line summary:** Change an anchor point's handle type — corner (no handles), mirror-angle (symmetric direction + length), mirror-angle-only (symmetric direction, independent length), or fully independent handles.

## Triggers
- Select a point + click a handle-type icon in the vector-edit secondary toolbar OR the right-panel-equivalent control (engine decision; corpus describes "mirroring options" under vector edit tools).
- Alt/Option + click a handle endpoint → toggles handle independence (breaks symmetry for that endpoint).
- Bend tool on an anchor → may convert corner to smooth interactively.

## Preconditions
- In vector edit mode.
- One or more anchor points selected.

## Inputs
- Trigger only (for discrete toggle) OR handle drag (for Bend interactive).

## Behavior
1. Determine new handle type:
   - **Corner** — `handleIn = null`, `handleOut = null`
   - **Mirror angle + length** — `handleIn = -handleOut`
   - **Mirror angle only** — opposite direction, independent length
   - **Independent** — no coupling
2. Update the point's handles per the new type.
3. If converting away from corner, synthesize default handle lengths based on neighboring segment tangents.

## Outputs
- **Scene graph changes:** point's handle fields updated.

## UI feedback
- Canvas: handles appear / disappear / change length.
- Adjacent path segments re-render.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/toolbar.md` → secondary-toolbar-vector-edit-mode

## Semantic event(s) candidate
- `toggle_vector_handle { layer_id, point_index, from_type, to_type, trigger: "toolbar_button" | "alt_click_handle" | "bend_tool_drag" }`

## Source articles
- `edit-vector-layers`
- `vector-networks`

## Notes / gaps
- Variable width / shape builder — `visual-only` (plan/00 §3 — advanced vector features). Not covered in this file.
- Exact icon placement of handle-type controls varies across Figma versions. Treat as part of vector-edit secondary toolbar.
