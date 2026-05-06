# Boolean subtract

- **Category:** boolean
- **One-line summary:** Subtract overlapping areas of upper layers from the bottom layer of the selection.

## Triggers
- Selection ≥ 2 supported layers + shortcut:
  - Mac: `⌥ ⇧ S`
  - Windows: `Alt Shift S`
- Right sidebar sub-header → Boolean operations dropdown → **Subtract selection**.
- Right-click → Boolean operations → **Subtract selection**.

## Preconditions
- 2+ supported layers selected.

## Inputs
- Shortcut OR menu choice.

## Behavior
1. Boolean group created.
2. Resulting geometry: bottom layer's path with overlapping regions of upper layers removed.
3. Fill / stroke / effects taken from the **bottom-most** layer (per `boolean-operations`).
4. If result has both inner and outer edges, strokes/effects apply to both.

## Outputs
- **Scene graph changes:** boolean-group node; original layers reparented as children.
- **Selection changes:** selection = boolean group.

## UI feedback
- Layers panel: new "Subtract" group.
- Canvas: subtracted shape rendered.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → sub-header → boolean-ops dropdown

## Semantic event(s) candidate
- `boolean_subtract { layer_ids, result_id, trigger }`

## Source articles
- `boolean-operations`
