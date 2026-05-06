# Boolean exclude

- **Category:** boolean
- **One-line summary:** Remove the overlapping areas, keeping only the non-overlapping parts of the selected layers.

## Triggers
- Selection ≥ 2 supported layers + shortcut:
  - Mac: `⌥ ⇧ E`
  - Windows: `Alt Shift E`
- Right sidebar sub-header → Boolean operations → **Exclude selection**.
- Right-click → Boolean operations → **Exclude selection**.

## Preconditions
- 2+ supported layers selected.

## Inputs
- Shortcut OR menu choice.

## Behavior
1. Boolean group created.
2. Resulting geometry: symmetric difference (union minus intersection).
3. Fill / stroke / effects taken from the **topmost** layer.
4. If result has both inner and outer edges, strokes/effects apply to both.

## Outputs
- **Scene graph changes:** boolean-group node; original layers reparented.
- **Selection changes:** selection = boolean group.

## UI feedback
- Layers panel: new "Exclude" group.
- Canvas: result shape.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → sub-header → boolean-ops dropdown

## Semantic event(s) candidate
- `boolean_exclude { layer_ids, result_id, trigger }`

## Source articles
- `boolean-operations`
