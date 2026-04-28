# Add fill

- **Category:** fills
- **One-line summary:** Add a new fill row to a layer's fills array (default solid color, default opacity 100%).

## Triggers
- Right sidebar **Fill** section header → click `+` plus icon.
- (Stroke equivalent lives in stroke section — separate spec.)

## Preconditions
- Selection non-empty.
- Selected layer type supports fills (shapes, frames, text, images, vectors).

## Inputs
- Pointer click on `+`.

## Behavior
1. A new fill row appended to each selected layer's `fills` array.
2. Default type is solid; default color may be the picker's last-used color or a per-Figma default.
3. Color picker may auto-open anchored to the new swatch (per `guide-to-fills` "By default, Figma adds a solid fill. Click on the fill swatch to open the color picker.").

## Outputs
- **Scene graph changes:** each selected layer's `fills` array gains an entry.
- **Selection changes:** none.

## UI feedback
- New fill row appears in the Fill section.
- Canvas re-renders the layer with the additional fill stacked on top.

## Side effects
- Undo stack: one entry per add (regardless of multi-select count).

## Related UI schema entries
- `regions/right-properties.md` → fill-section → plus button

## Semantic event(s) candidate
- `add_fill { layer_ids: [...], fill_index, default_color, trigger: "panel_plus" }`

## Source articles
- `guide-to-fills`

## Notes / gaps
- Initial color: corpus does not specify — could be black, picker last value, or per-Figma policy. Implementer picks.
- Whether picker auto-opens on `+` is documented as "Click on the fill swatch to open the color picker" (one extra click after add). Treat picker opening as a user action, not automatic.
