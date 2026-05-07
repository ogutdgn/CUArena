# Recent colors history

- **Category:** color
- **One-line summary:** Picker shows a row of recently-used colors; clicking one re-applies it without retyping.

## Triggers
- Color picker open — pointer click on a swatch in the recent-colors row.

## Preconditions
- Picker open.
- One or more colors used previously in the session (history non-empty).

## Inputs
- Pointer click on a recent-colors swatch.

## Behavior
1. Picker maintains an ordered list of recently-applied solid colors.
2. The recents row renders these as small swatches.
3. Clicking a swatch applies that color as the current color (commits like any other picker edit).

## Outputs
- **Scene graph changes:** target property color updated to the chosen recent.
- **Selection changes:** none.

## UI feedback
- Picker numeric fields update.
- Canvas updates live.

## Side effects
- Undo stack: one entry on commit.
- The chosen color may be promoted to the front of the recents list.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → recent-colors-row

## Semantic event(s) candidate
- `apply_recent_color { layer_ids, target, fill_index?, color, slot_index, trigger: "recents_swatch_click" }`

## Source articles
- `update-fills-using-the-color-picker` (item 11: "View and select colors in the current file, or from libraries added to the file.")

## Notes / gaps
- Corpus does not enumerate recents-row size, ordering rules, persistence (per-session vs per-file vs per-account), or whether gradient/image fills also surface there.
- Real Figma renders both **document colors** (colors used in the current file) and **library colors** (from enabled libraries) in the bottom area of the picker. See `document-colors.md` and `library-colors-browser.md` for those — recents may share or differ.
