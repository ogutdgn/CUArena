# Convert stroke to path

- **Category:** vector
- **One-line summary:** Convert a layer's stroke into a vector outline — useful for further editing the stroke as a shape.

## Triggers
- Selection has stroke + Right-click → **Outline stroke** OR equivalent menu entry.
- Shortcut: `⇧ ⌘ O` (Mac) / `Ctrl Shift O` per `convert-strokes-to-vector-paths` (cross-check; also collides with show-outlines `Cmd Shift O`).

## Preconditions
- Selected layer has a stroke applied.

## Inputs
- Menu choice or shortcut.

## Behavior
1. The stroke (with weight, alignment, dashed pattern, end-points if any) is converted into a closed vector path.
2. The resulting path replaces the original layer's stroke (the stroke property is removed; the new vector covers the same area).
3. Original fill is preserved as a separate vector layer (or merged — implementation choice; confirm in source article).

## Outputs
- **Scene graph changes:** original stroke removed; new vector layer represents what the stroke painted.
- **Selection changes:** selection = the new vector layer.

## UI feedback
- Layer panel: structure changes accordingly.
- Canvas: visual unchanged; underlying representation changed.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `convert_stroke_to_path { layer_ids, new_layer_ids, trigger: "menu" | "shortcut" }`

## Source articles
- `convert-strokes-to-vector-paths`

## Notes / gaps
- Naming: real Figma menu may say "Outline stroke". Confirm exact label from source article.
- Whether shortcut conflict with show-outlines `Cmd Shift O` is real — corpus has both keys mapped; one must be different. Check `use-figma-products-with-a-keyboard` for canonical sheet.
