# Set effects

- **Category:** properties
- **One-line summary:** Add, remove, or edit layer effects — drop shadow, inner shadow, layer blur, background blur — on selected layer(s).

## Triggers
- Right-sidebar Effects section:
  - `+` → add new effect (opens effect-type picker)
  - Click an effect row to edit its parameters
  - `…` → remove / reorder
  - Eye icon per effect → toggle visibility

## Preconditions
- Selection is non-empty.

## Inputs
- Effect type picker selection: Drop shadow / Inner shadow / Layer blur / Background blur / (Noise / Texture / Glass — `visual-only`).
- Numeric inputs: X / Y offset, Blur, Spread, Color.

## Behavior

**Add effect:**
1. Click `+`.
2. Effect-type picker opens.
3. User picks type → new effect appended to `effects` array with default params.

**Edit effect:**
1. Click effect row to expand / open popover.
2. Edit fields.

**Remove effect:**
1. `…` → Remove.

## Outputs
- **Scene graph changes:** selected layers' `effects` array updated.
- **Selection changes:** none.

## UI feedback
- Canvas: shadow / blur rendering updates live.
- Panel: row updates.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → effects-section

## Semantic event(s) candidate
- `add_effect { layer_ids, effect_index, type: "drop_shadow" | "layer_blur" | ..., default_params, trigger }`
- `remove_effect { layer_ids, effect_index, trigger }`
- `set_effect_params { layer_ids, effect_index, from_params, to_params, trigger }`
- `toggle_effect_visibility { layer_ids, effect_index, to_visible, trigger }`

## Source articles
- `apply-effects-to-layers`

## Notes / gaps
- In scope: **drop shadow + layer blur** (per plan/00 §2). Functional.
- Visual-only: **inner shadow, background blur, noise, texture, glass**. The picker renders these entries; picking one creates a visually-inert effect row.
- Advanced shadow params (color-stops, specific blend modes for effects) not detailed; implement the common X/Y/blur/spread/color set.
