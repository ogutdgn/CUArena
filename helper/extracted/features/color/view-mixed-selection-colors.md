# View / adjust colors in a mixed selection

- **Category:** color
- **One-line summary:** When a multi-selection has different fill/stroke colors, the right sidebar shows a **Selection colors** section listing each distinct color; clicking a swatch opens the picker scoped to all layers using that color.

## Triggers
- Multi-select layers whose fill or stroke colors differ.
- Right sidebar **Selection colors** section becomes visible (above per-property sections).
- Click a swatch in that section.

## Preconditions
- Multi-selection (≥ 2 layers).
- At least 2 selected layers share no single fill/stroke color (otherwise the standard Fill/Stroke sections show that color directly).

## Inputs
- Pointer click on a Selection-colors swatch → opens picker scoped to that color.
- Picker edits propagate to every selected layer that was using the original color.

## Behavior
1. Mock builds a unique-color list across the selection's fills + strokes.
2. Each unique color renders as a row with a swatch + small "this many layers use this" indicator.
3. Click → picker opens; edits update **all** the using layers atomically.
4. Closing the picker = one undo entry covering all those layers.

## Outputs
- **Scene graph changes:** every layer in the selection that used the original color is updated to the new color.
- **Selection changes:** none.

## UI feedback
- The Selection colors section row's swatch updates to the new value.
- Canvas re-renders all matching layers.

## Side effects
- Undo stack: one entry covering all affected layers.

## Related UI schema entries
- `regions/right-properties.md` → selection-colors-section
- `regions/floating-overlays.md` → color-picker

## Semantic event(s) candidate
- `set_selection_color { affected_layer_ids: [...], from_color, to_color, source_property: "fill" | "stroke", trigger: "selection_colors_picker" }`

## Source articles
- `view-and-adjust-colors-in-a-mixed-selection`

## Notes / gaps
- Section is only visible on multi-mixed selections — the `state-matrix.md` already encodes this.
- If a layer uses the same color in multiple fills, the mapping needs to update each occurrence — corpus is ambiguous; treat all matching occurrences as updated.
