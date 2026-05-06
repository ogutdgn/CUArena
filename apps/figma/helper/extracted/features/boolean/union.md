# Boolean union

- **Category:** boolean
- **One-line summary:** Combine two or more selected layers into a single boolean group whose outer path is the merged outer edges of the selection.

## Triggers
- Selection ≥ 2 supported layers + shortcut:
  - Mac: `⌥ ⇧ U`
  - Windows: `Alt Shift U`
- Right sidebar sub-header → Boolean operations dropdown → **Union selection**.
- Right-click on selection → Boolean operations → **Union selection**.

## Preconditions
- 2+ selected supported layers (shape layers, vector paths, text layers). Sections and frames are not supported.

## Inputs
- Shortcut OR menu choice.

## Behavior
1. Boolean group created (non-destructive — original layers preserved as children of the group).
2. Outer path = union of all input paths (merged outer edges).
3. Resulting fill / stroke / effects taken from the **topmost** layer in the original z-order.
4. Strokes and effects apply to the boolean group's outer path.
5. The original layers remain editable (position, dimensions, rotation, corner radius); fill/stroke/effects/opacity of children are no longer editable individually.

## Outputs
- **Scene graph changes:** new boolean-group node; selected layers reparented as its children.
- **Selection changes:** selection = the boolean group.

## UI feedback
- Layers panel: new "Union" group containing the original layers.
- Canvas: merged outline rendered.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → sub-header → boolean-ops dropdown
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `boolean_union { layer_ids: [...], result_id, trigger: "shortcut" | "menu" | "context_menu" }`

## Source articles
- `boolean-operations`

## Notes / gaps
- Article notes: "Boolean operations now use a layer's stroke and fill to calculate the geometry of the resulting shape." Mock implementation can ignore stroke-affecting-geometry simplification on first pass.
