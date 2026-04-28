# Document colors palette

- **Category:** color
- **One-line summary:** The picker surfaces every color currently used on the canvas in the current file as a clickable swatch row.

## Triggers
- Color picker open — pointer click on a swatch under the **Document colors** section.

## Preconditions
- Picker open.
- File has at least one applied solid color elsewhere.

## Inputs
- Pointer click on a swatch.

## Behavior
1. Picker scans the current file's used colors (fills, strokes, effects, page bg, etc.).
2. These are rendered as a swatch row near the bottom of the picker.
3. Clicking applies the chosen color to the current target property.

## Outputs
- **Scene graph changes:** target property color updated.
- **Selection changes:** none.

## UI feedback
- Picker numeric fields and canvas update live.

## Side effects
- Undo stack: one entry on commit.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → document-colors-section

## Semantic event(s) candidate
- `apply_document_color { layer_ids, target, fill_index?, color, source_layer_ids: [...], trigger: "doc_colors_swatch_click" }`

## Source articles
- `update-fills-using-the-color-picker` (item 11)

## Notes / gaps
- The exact algorithm for de-duplication, sort order, and grouping (e.g. "All colors used in this file" vs grouped by fill type) is not enumerated in the corpus.
- Whether gradient stops contribute their stop colors to this list is not stated.
