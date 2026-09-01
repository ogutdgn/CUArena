# Use shape builder tool

- **Category:** vector
- **One-line summary:** Interactively merge / subtract regions of overlapping shapes by dragging across them.

## Triggers
- Select 2+ overlapping shape / vector layers.
- Press `Enter` to enter vector edit mode.
- Select **Shape builder** from the secondary toolbar.
- (Also via Actions menu).

## Preconditions
- 2+ overlapping shape / vector layers, all selected.
- Vector edit mode active.

## Inputs
- Pointer drag across regions:
  - **Drag across (no modifier)** — combines regions.
  - **Drag with `⌥ Option` / `Alt`** — subtracts regions.

## Behavior
1. Engine pre-computes overlap regions of the selected shapes.
2. Drag merges (or subtracts with Alt) regions along the drag path.
3. Result is a custom vector network combining/subtracting the chosen regions.
4. Useful for icon construction.

## Outputs
- **Scene graph changes:** new vector layer combining the selected regions; original shapes may be consumed (destructive, per the tool's purpose).
- **Selection changes:** selection = new vector.

## UI feedback
- Hovered region highlights as you drag.
- Vector edit secondary toolbar shows tool active.

## Side effects
- Undo stack: one entry per shape-builder commit (the drag).

## Related UI schema entries
- `regions/toolbar.md` → secondary toolbar (vector edit) → shape-builder

## Semantic event(s) candidate
- `apply_shape_builder { layer_ids, drag_path, mode: "merge" | "subtract", result_id }`

## Source articles
- `create-custom-shapes-with-the-shape-builder-tool`
- `edit-vector-layers`

## Notes / gaps
- Exact modifier (Alt vs Shift) for subtract may vary; confirm in the source article.
