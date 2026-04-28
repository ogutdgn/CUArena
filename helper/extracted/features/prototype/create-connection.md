# Create prototype connection

- **Category:** prototype
- **One-line summary:** Connect a layer or hotspot to another frame as a destination on a trigger; visualized as an arrow on the canvas.

## Triggers
- Switch to **Prototype** tab in right sidebar (`Shift E`).
- Hover the source layer → blue connector dot appears → drag to target frame.

## Preconditions
- Prototype tab active.
- Source and target are valid (frame, hotspot, component).

## Inputs
- Pointer drag from source's connector dot to target.

## Behavior
1. Connection stored with `trigger`, `action`, `destination`, `animation`.
2. Visualized as a blue arrow from source to target on canvas.
3. Connections render only on the Prototype tab.

## Outputs
- **Scene graph changes:** prototype graph gains an edge.
- **Selection changes:** new edge selected.

## UI feedback
- Arrow on canvas.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/canvas-overlays.md` → prototype-arrow, prototype-hotspot

## Semantic event(s) candidate
- `create_prototype_connection { source_layer_id, target_layer_id, trigger_type, action_type, trigger }`

## Source articles
- `connect-your-prototype`
- `guide-to-prototyping-in-figma`
- `view-prototype-connections`
