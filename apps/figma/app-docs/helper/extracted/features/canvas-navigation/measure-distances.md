# Measure distances between layers

- **Category:** canvas-navigation
- **One-line summary:** Hold Option/Alt while hovering between two layers (or with one selected) to display measurements between them.

## Triggers
- Selection on a layer.
- Hold `⌥ Option` (Mac) / `Alt` (Win) and hover another layer.

## Preconditions
- A layer is selected.

## Inputs
- Modifier hold + hover.

## Behavior
1. Red guide lines and numeric labels appear showing distances between selected layer's edges and the hovered layer's edges (top/bottom/left/right).
2. Measurements update live as the cursor moves.
3. Toolbar **Measurement** tool (`Shift M`) places persistent measurement annotations.

## Outputs
- **Scene graph changes:** none for ephemeral; persistent measurements added when using Measurement tool.
- **Selection changes:** none.

## UI feedback
- Red lines + labels.

## Side effects
- Undo stack: only when persistent measurement is added.

## Related UI schema entries
- `regions/canvas-overlays.md` → measure-distances-overlay

## Semantic event(s) candidate
- `measure_distance_hover { selected_layer_id, hovered_layer_id, measurements }`
- `add_measurement_annotation { from_layer, to_layer, distances, trigger: "measurement_tool" }`

## Source articles
- `measure-distances-between-layers`
