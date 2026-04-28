# Library colors browser

- **Category:** color
- **One-line summary:** Within the color picker, browse colors (styles + variables) from libraries enabled for the current file.

## Triggers
- Color picker open — click the **Libraries** tab.

## Preconditions
- Picker open.
- One or more libraries enabled for the file (per `add-or-remove-a-library-from-a-design-file`).

## Inputs
- Pointer click on a swatch.
- Optional search box to filter.

## Behavior
1. The Libraries tab lists every color style and color variable exposed by enabled libraries.
2. Clicking a swatch applies the style/variable as a binding (see `apply-color-style.md`).
3. If the search box is present, typing filters the list.

## Outputs
- **Scene graph changes:** target color bound to the chosen style/variable.
- **Selection changes:** none.

## UI feedback
- Picker shows the applied style/variable chip.

## Side effects
- Undo stack: one entry per apply.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → libraries-tab + search

## Semantic event(s) candidate
- `apply_library_color { layer_ids, target, fill_index?, library_id, asset_id, asset_type: "style" | "variable", trigger: "picker_libraries_click" }`

## Source articles
- `apply-styles-to-layers-and-objects`
- `add-or-remove-a-library-from-a-design-file`
- `update-fills-using-the-color-picker` (item 1: "Choose a custom color, or browse color styles and variables from your libraries.")
- `enable-access-to-libraries-in-your-drafts`
- `swap-libraries`

## Notes / gaps
- Whether the picker shows variables and styles in two distinct sub-sections or one combined list is not pinned by docs.
- Corpus does not specify search-field behavior (substring vs fuzzy).
