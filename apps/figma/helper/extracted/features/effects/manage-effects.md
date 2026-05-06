# Manage effects (reorder, remove, toggle visibility)

- **Category:** effects
- **One-line summary:** Standard per-effect controls — eye toggle, drag handle to reorder, `…` menu, `-` to remove.

## Triggers
- Right sidebar Effects section row → eye / drag / `…` / `-` controls.

## Preconditions
- Layer has one or more effects.

## Inputs
- Click eye / drag handle / menu / minus.

## Behavior
- **Eye**: toggles `visible` flag on the effect.
- **Drag handle**: reorders effects (top of the panel = drawn last).
- **`…` menu**: per-effect options (move up/down, paste over, etc.).
- **`-`**: removes the effect.

## Outputs
- **Scene graph changes:** `effects` array mutated.
- **Selection changes:** none.

## UI feedback
- Effect row updates; canvas re-renders.

## Side effects
- Undo stack: one entry per action.

## Related UI schema entries
- `regions/right-properties.md` → effects-section

## Semantic event(s) candidate
- `toggle_effect_visibility { layer_ids, effect_index, to_state, trigger }`
- `reorder_effect { layer_ids, from_index, to_index }`
- `remove_effect { layer_ids, effect_index, trigger }`

## Source articles
- `apply-effects-to-layers`
