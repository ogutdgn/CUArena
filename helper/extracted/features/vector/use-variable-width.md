# Use variable width tool

- **Category:** vector
- **One-line summary:** Add per-point width controls along a stroke to vary stroke thickness along the path.

## Triggers
- Vector edit mode + secondary toolbar **Variable width**.

## Preconditions
- Vector edit mode active.
- Layer has a stroke.
- Stroke is **not** dynamic / dashed (per `edit-vector-layers` notes).
- Vector network is not branching (split via right-click → **Split vector** if needed).

## Inputs
- Hover the stroke → pink width handle appears.
- Click to add a new width point.
- Drag the handle to expand/contract stroke width at that point, OR enter a numeric value in the field.
- `Control` (Mac) / `Ctrl` (Win) — temporarily disable snapping.
- `Shift` + click — multi-select width points.
- `Delete` to remove selected width points.

## Behavior
1. Width points snap to: vector points, midpoint between two vector points, midpoint between two width points.
2. Width can taper between adjacent width points.

## Outputs
- **Scene graph changes:** stroke object gains a `width_points: [{ position, width }]` array.
- **Selection changes:** width point may be sub-selected.

## UI feedback
- Pink handles along stroke.
- Stroke renders with variable thickness.

## Side effects
- Undo stack: per-action entries.

## Related UI schema entries
- `regions/toolbar.md` → secondary toolbar (vector edit) → variable-width

## Semantic event(s) candidate
- `add_width_point { layer_id, position, width }`
- `move_width_point { layer_id, point_index, from_position, to_position }`
- `set_width_point_width { layer_id, point_index, from_width, to_width }`
- `remove_width_point { layer_id, point_index }`

## Source articles
- `edit-vector-layers`
- `apply-and-adjust-stroke-properties` (width profiles cross-link)

## Notes / gaps
- Width-profile presets (smoothly tapered ends, etc.) are in `apply-and-adjust-stroke-properties`.
