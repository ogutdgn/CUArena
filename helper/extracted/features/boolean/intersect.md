# Boolean intersect

- **Category:** boolean
- **One-line summary:** Keep only the overlapping area of the selected layers.

## Triggers
- Selection ≥ 2 supported layers + shortcut:
  - Mac: `⌥ ⇧ I`
  - Windows: `Alt Shift I`
- Right sidebar sub-header → Boolean operations → **Intersect selection**.
- Right-click → Boolean operations → **Intersect selection**.

## Preconditions
- 2+ supported layers selected.

## Inputs
- Shortcut OR menu choice.

## Behavior
1. Boolean group created.
2. Resulting geometry: intersection of all input paths.
3. Fill / stroke / effects taken from the **topmost** layer.
4. Strokes/effects apply to outer path.
5. **Edge case:** if layers don't overlap, the result is empty — layers visually disappear from canvas until moved to overlap.

## Outputs
- **Scene graph changes:** boolean-group node; original layers reparented.
- **Selection changes:** selection = boolean group.

## UI feedback
- Layers panel: new "Intersect" group.
- Canvas: intersection shape (or empty if no overlap).

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → sub-header → boolean-ops dropdown

## Semantic event(s) candidate
- `boolean_intersect { layer_ids, result_id, trigger }`

## Source articles
- `boolean-operations`
